from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_service_level = fields.Boolean(
        implied_group='generic_service.group_use_service_level',
        string='Use Service Level'
    )
