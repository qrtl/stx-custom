from odoo import models, api
from odoo.exceptions import UserError
import base64
import uuid

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def analyze_with_openai_vision(self, attachment_id, prompt_text="この画像に何が写っていますか？"):
        attachment = self.browse(attachment_id)
        if not attachment or not attachment.datas:
            return "指定された添付ファイルが存在しないか、データがありません。"

        try:
            # base64エンコードされた画像URLを作成
            image_data = base64.b64decode(attachment.datas)
            base64_str = base64.b64encode(image_data).decode("utf-8")
            image_url = f"data:{attachment.mimetype};base64,{base64_str}"

            # セッションの作成
            session = self.env['openai.vision.session'].create({
                'name': f"Attachment Analysis: {attachment.name or str(uuid.uuid4())}",
                'model': 'gpt-4o-mini',
                'temperature': 0.7,
            })

            # メッセージをセッションに関連付けて作成
            Message = self.env['openai.vision.message']
            Message.create({
                'role': 'user',
                'type': 'text',
                'content': prompt_text,
                'sequence': 10,
                'input_session_id': session.id,
            })
            Message.create({
                'role': 'user',
                'type': 'image_url',
                'content': image_url,
                'sequence': 10,
                'input_session_id': session.id,
            })

            # OpenAI APIを呼び出し
            session.call_openAI()

            return session.response_text or session.response_refusal_message or "応答がありませんでした。"

        except Exception as e:
            return f"エラー: {str(e)}"
