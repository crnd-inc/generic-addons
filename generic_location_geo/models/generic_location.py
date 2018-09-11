from odoo import fields, models


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    longitude = fields.Float(
        digits=(16, 5))
    latitude = fields.Float(
        digits=(16, 5))
