from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    my_super_secret_42 = fields.Char(
        crypto_param='my.super.secret.42')


