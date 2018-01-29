# -*- coding: utf-8 -*-

from openerp import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'
    _inherit = 'mail.thread'
    _description = 'Generic Service'

    name = fields.Char(
        translate=True, required=True, index=True, track_visibility='always')
    active = fields.Boolean(
        default=True, index=True, track_visibility='onchange')
    description = fields.Text(translate=True)
