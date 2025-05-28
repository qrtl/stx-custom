{
    'name': 'ChatGPT Integration',
    'version': '1.0',
    'summary': 'Integrate ChatGPT with Odoo',
    'description': 'This module allows integration with ChatGPT by storing API keys in res_config and res_company.',
    'author': 'Your Company',
    'website': 'https://www.quartile.co',
    'category': 'Tools',
    'depends': ['base', 'base_setup', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/openai_vision_message.xml',
        'views/openai_vision_session.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
