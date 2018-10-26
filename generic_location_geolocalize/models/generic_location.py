from odoo import api, models
from odoo.addons.base_geolocalize.models.res_partner import (
    geo_find,
    geo_query_address,
)


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    @classmethod
    def _geo_localize(cls, apikey, street='', zip_code='', city='',
                      state='', country=''):
        search = geo_query_address(
            street=street, zip=zip_code, city=city,
            state=state, country=country)
        result = geo_find(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        apikey = self.env['ir.config_parameter'].sudo().get_param(
            'google.api_key_geocode')
        for record in self.with_context(lang='en_US'):
            result = record._geo_localize(
                apikey,
                street=record.street,
                zip_code=record.zip,
                city=record.city,
                state=record.state_id.name,
                country=record.country_id.name)
            if result:
                record.write({
                    'latitude': result[0],
                    'longitude': result[1]
                })
        return True
