from odoo import api, models
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find,
    geo_query_address,
)


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    @api.multi
    def geo_localize(self):
        for record in self.with_context(lang='en_US'):
            result = geo_find(geo_query_address(
                street=record.street,
                zip=record.zip,
                city=record.city,
                state=record.state_id.name,
                country=record.country_id.name
            ))

            if result is None:
                result = geo_find(geo_query_address(
                    city=record.city,
                    state=record.state_id.name,
                    country=record.country_id.name
                ))

            if result:
                record.write({
                    'latitude': result[0],
                    'longitude': result[1]
                })
        return True
