from odoo import models, fields


class GenericLocationMixin(models.AbstractModel):
    _name = 'generic.location.mixin'

    location_id = fields.Many2one('generic.location')
