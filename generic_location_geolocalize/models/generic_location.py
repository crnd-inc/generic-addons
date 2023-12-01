import json
from odoo import models, fields, api


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    geolocation_json = fields.Char(
        compute='_compute_geolocation_json',
        inverse='_inverse_geolocation_json')

    @api.depends('latitude', 'longitude')
    def _compute_geolocation_json(self):
        for rec in self:
            rec.geolocation_json = json.dumps({
                'lat': round(rec.latitude, 5),
                'lng': round(rec.longitude, 5)
            }, ensure_ascii=False)

    def _inverse_geolocation_json(self):
        for rec in self:
            geolocation = json.loads(rec.geolocation_json)
            rec.latitude = geolocation['lat']
            rec.longitude = geolocation['lng']

    @api.model
    def _geo_localize(self, street='', zip_code='', city='',
                      state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(
            street=street,
            zip=zip_code,
            city=city,
            state=state,
            country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(
                city=city,
                state=state,
                country=country)
            result = geo_obj.geo_find(
                search,
                force_country=country)
        return result

    def geo_localize(self):
        for rec in self.with_context(lang='en_US'):
            street = (
                "%s, %s" % (rec.street, rec.street2)
                if rec.street2 else rec.street
            )
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
