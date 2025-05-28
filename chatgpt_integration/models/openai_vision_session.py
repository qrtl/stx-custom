import json
from odoo import models, fields, api
from odoo.exceptions import UserError
from openai import OpenAI
from collections import defaultdict


class OpenAISession(models.Model):
    _name = 'openai.vision.session'
    _description = 'openai Vision Session'

    name = fields.Char(required=True, string="Session Name")
    model = fields.Selection([
        ('gpt-4o', 'GPT-4o'),
        ('gpt-4o-mini', 'GPT-4o-mini'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ], default='gpt-4o-mini', required=True)
    temperature = fields.Float(default=0.7, string="Temperature")
    input_message_ids = fields.One2many('openai.vision.message', 'input_session_id', string="Input Messages")
    response_message_ids = fields.One2many('openai.vision.message', 'response_session_id',string="Response Messages")
    response_refusal_message = fields.Text(string="Refusal Reason", readonly=True)
    response_text = fields.Text(string="Response", readonly=True)
    response_format_enabled = fields.Boolean(string="Use Structured Output (JSON Schema)", default=False)
    response_format_schema = fields.Text(
    string="Response Format Schema (JSON)",
    default='{"name": "math_response", "strict": true, "schema": {}}')

    @api.onchange('response_format_schema','response_format_strict')
    def _onchange_response_format_schema(self):
        for record in self:
            if record.response_format_enabled:
                try:
                    json.loads(record.response_format_schema or "{}")
                except json.JSONDecodeError as e:
                    raise UserError("The JSON schema is invalid:\n%s" % str(e))

    @api.model
    def call_openAI(self):
        api_key = self.env.company.openai_api_key
        if not api_key:
            raise UserError("OpenAI API key is not configured")

        client = OpenAI(api_key=api_key)

        for record in self:
            grouped = defaultdict(list)
            for c in record.input_message_ids.sorted("sequence"):
                key = (c.sequence, c.role)
                grouped[key].append(c)

            messages = []
            sorted_keys = sorted(grouped.keys(), key=lambda k: k[0])
            for seq, role in sorted_keys:
                roles = {c.role for c in grouped[(seq, role)]}
                if len(roles) != 1:
                    raise UserError(
                        f"Multiple roles found at sequence: {roles}")
                messages.append({
                    "role": role,
                    "content": [c.to_openai_dict() for c in grouped[(seq, role)] if c.content and c.content.strip()]
                })
            request_payload = {
                "model": record.model,
                "messages": messages,
                "temperature": record.temperature,
            }
            # consider about the model
            if record.response_format_enabled and record.model in ['gpt-4o-mini']:
                try:
                    user_schema = json.loads(record.response_format_schema or "{}")
                except json.JSONDecodeError as e:
                    raise UserError("The JSON schema is invalid:\n%s" % str(e))
                request_payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": user_schema,
                }
            try:
                response = client.chat.completions.create(**request_payload)
                message = response.choices[0].message
                role = message.role or "assistant"
                content = message.content
                record.response_refusal_message = False
                if isinstance(content, str):
                    record.response_text = content.strip()
                    sequence = max(record.input_message_ids.mapped('sequence') or [10]) + 10
                    record.response_message_ids.create({
                        'response_session_id': record.id,
                        'role': role,
                        'type': 'text',
                        'content': content.strip(),
                        'sequence': sequence,
                    })
                elif isinstance(content, list):
                    sequence = max(record.response_session_id.mapped('sequence') or [0])
                    for item in content:
                        if item.get("type") == "refusal":
                            record.response_refusal_message = item.get("refusal", "Refused")
                            continue
                        msg_type = item.get("type")
                        msg_content = (
                            item.get("text") if msg_type == "text"
                            else item.get("image_url", {}).get("url")
                        )
                        if msg_type and msg_content:
                            sequence += 1
                            record.response_message_ids.create({
                                'response_session_id': record.id,
                                'role': role,
                                'type': msg_type,
                                'content': msg_content,
                                'sequence': sequence,
                            })
            except Exception as e:
                raise UserError(f"OpenAI error: {e}")
