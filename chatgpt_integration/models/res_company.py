from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    openai_api_key = fields.Char(string='OpenAI API Key')
