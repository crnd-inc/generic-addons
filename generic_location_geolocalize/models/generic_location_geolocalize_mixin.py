from odoo import models


class GenericLocationGeolocalizeMixin(models.AbstractModel):
    _name = 'generic.location.geolocalize.mixin'
    _inherit = 'generic.location.mixin'
    _description = 'Generic Location Geolocalize Mixin'

    def geo_localize(self):
        if self.location_id:
            return self.location_id.geo_localize()
        return False
