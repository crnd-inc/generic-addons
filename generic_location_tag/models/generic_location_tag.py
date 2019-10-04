from odoo import models


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'generic.location',
        'generic.tag.mixin',
    ]
