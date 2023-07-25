from odoo import models, fields


class GenericLocationGeolocalizeMixin(models.AbstractModel):
    _name = 'generic.location.geolocalize.mixin'
    _inherit = 'generic.location.mixin'
    _description = 'Generic Location Geolocalize Mixin'

    geolocation_json = fields.Char(related='location_id.geolocation_json',
                                   readonly=False)

    def geo_localize(self):
        if self.location_id:
            return self.location_id.geo_localize()
        return False
