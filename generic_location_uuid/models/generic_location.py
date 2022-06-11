import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'generic.location',
        'generic.mixin.uuid',
    ]
    uuid = fields.Char(
        index=True, required=True, readonly=True,
        size=38, default='/', copy=False, string='UUID')

    _sql_constraints = [
        ('uuid_uniq',
         'UNIQUE (uuid)',
         'UUID must be unique.'),
    ]
