from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_hierarchical_locations = fields.Boolean(
        implied_group='generic_location.group_use_hierarchical_locations',
        string='Use hierarchical locations'
    )
