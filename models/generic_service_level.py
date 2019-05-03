import logging

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slugify

_logger = logging.getLogger(__name__)


class GenericServiceLevel(models.Model):
    _name = 'generic.service.level'
    _inherit = 'mail.thread'
    _order = 'sequence, name'
    _description = 'Generic Service Level'

    name = fields.Char(
        translate=True, required=True, index=True, track_visibility='onchange')
    code = fields.Char(index=True, required=True, track_visibility='onchange')
    description = fields.Text(translate=True)
    active = fields.Boolean(
        default=True, index=True, track_visibility='onchange')
    sequence = fields.Integer(index=True, default=5)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',
         'Name of Service Level must be unique.'),
        ('code_uniq', 'UNIQUE (code)',
         'Code of Service Level must be unique.'),
        ('code_ascii_only', r"CHECK (code ~ '^[a-zA-Z0-9\-_]*$')",
         'Service Level code must be ascii only, check it, please.'),
    ]

    @api.onchange('name')
    def _onchange_mixin_name_set_code(self):
        for record in self:
            record.code = slugify(record.name or '', max_length=0)
