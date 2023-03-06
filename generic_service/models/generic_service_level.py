import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class GenericServiceLevel(models.Model):
    _name = 'generic.service.level'
    _inherit = [
        'mail.thread',
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'generic.mixin.track.changes'
    ]
    _order = 'sequence, name'
    _description = 'Generic Service Level'

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    description = fields.Text(translate=True)
    active = fields.Boolean(
        default=True, index=True, tracking=True)
    sequence = fields.Integer(index=True, default=5)
