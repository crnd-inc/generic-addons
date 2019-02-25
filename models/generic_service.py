from odoo import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'
    _inherit = 'mail.thread'
    _description = 'Generic Service'
    _order = 'sequence, name'

    name = fields.Char(
        translate=True, required=True, index=True, track_visibility='always')
    active = fields.Boolean(
        default=True, index=True, track_visibility='onchange')
    description = fields.Text(translate=True)
    sequence = fields.Integer(index=True, default=5)
