from odoo import models, fields


import logging
_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    def _default_country_id(self):
        company = self._default_company()
        return company.country_id

    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one(
        'res.country', string='Country', default=_default_country_id)
