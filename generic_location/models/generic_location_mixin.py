from odoo import models, fields


class GenericLocationMixin(models.AbstractModel):
    _name = 'generic.location.mixin'
    _description = 'Generic Location Mixin'

    location_id = fields.Many2one('generic.location')
