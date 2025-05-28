from odoo import models, fields, api

class OpenAIVisionMessage(models.Model):
    _name = 'openai.vision.message'
    _description = 'OpenAI Vision Message Line'

    role = fields.Selection([
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System")
    ], default='user', required=True)
    type = fields.Selection([
        ("text", "Text"),
        ("image_url", "Image URL")
    ], default='text', required=True)
    input_session_id = fields.Many2one('openai.vision.session',string="Input Session")
    response_session_id = fields.Many2one('openai.vision.session',string="Respose Session")
    content = fields.Text(string="Content")
    sequence = fields.Integer(default=10, string="Sequence")

    @api.model
    def to_openai_dict(self):
        if self.type == "text":
            return {"type": "text", "text": self.content.strip() if self.content else ""}
        elif self.type == "image_url":
            return {
                "type": "image_url",
                "image_url": {
                    "url": self.content.strip() if self.content else "",
                    "detail": "auto"
                }
            }
