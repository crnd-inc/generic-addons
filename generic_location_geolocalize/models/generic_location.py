from odoo import models, api
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find,
    geo_query_address,
)


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    @api.model
    def _geo_localize(self, street='', zip_code='', city='',
                      state='', country=''):
        apikey = self.env['ir.config_parameter'].sudo().get_param(
            'google.api_key_geocode')
        search = geo_query_address(
            street=street, zip=zip_code, city=city,
            state=state, country=country)
        result = geo_find(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find(search, apikey)
        return result

    def geo_localize(self):
        for rec in self.with_context(lang='en_US'):
            street = (rec.street, rec.street2) if rec.street2 else rec.street
            result = self._geo_localize(
                street=street,
                zip_code=rec.zip,
                city=rec.city,
                state=rec.state_id.name,
                country=rec.country_id.name)
            if result:
                rec.write({
                    'latitude': result[0],
                    'longitude': result[1]
                })
        return True
