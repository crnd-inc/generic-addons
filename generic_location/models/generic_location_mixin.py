from odoo import models, fields


class GenericLocationMixin(models.AbstractModel):
    _name = 'generic.location.mixin'
    _description = 'Generic Location Mixin'

    location_id = fields.Many2one('generic.location')

    country_id = fields.Many2one(related='location_id.country_id')
    state_id = fields.Many2one(related='location_id.state_id')
    city = fields.Char(related='location_id.city')
    zip = fields.Char(related='location_id.zip')
    street = fields.Char(related='location_id.street')
    street2 = fields.Char(related='location_id.street2')

    longitude = fields.Float(related='location_id.longitude')
    latitude = fields.Float(related='location_id.latitude')
