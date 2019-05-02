import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GenericServiceLevel(models.Model):
    _name = 'generic.service.level'
    _inherit = 'mail.thread'
    _description = 'Generic Service Level'

    name = fields.Char(
        translate=True, required=True, index=True, track_visibility='onchange')
    code = fields.Char(index=True, required=True, track_visibility='onchange')
    description = fields.Text(translate=True)
    active = fields.Boolean(
        default=True, index=True, track_visibility='onchange')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',
         'Name of Service Level must be unique.'),
        ('code_uniq', 'UNIQUE (code)',
         'Code of Service Level must be unique.'),
        ('code_ascii_only', r"CHECK (code ~ '^[a-zA-Z0-9\-_]*$')",
         'Service Level code must be ascii only, check it, please.'),
    ]

    @api.onchange('name')
    def onchange_name_set_code(self):
        for rec in self:
            rec.code = rec.name
