from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    service_level_id = fields.Many2one(
        'generic.service.level', ondelete='restrict')
