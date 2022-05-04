from odoo import models, fields


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'generic.location',
        'generic.mixin.uuid',
    ]

    uuid = fields.Char(required=True, readonly=True)

    _sql_constraints = [
        ('uuid_uniq',
         'UNIQUE (uuid)',
         'uuid must be unique.'),
    ]
