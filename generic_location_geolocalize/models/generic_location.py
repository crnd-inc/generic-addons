from odoo import models, api


class GenericLocation(models.Model):
    _inherit = 'generic.location'

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
