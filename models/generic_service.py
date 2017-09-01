# -*- coding: utf-8 -*-

from openerp import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'

    name = fields.Char(translate=True, required=True, index=True)
    active = fields.Boolean(default=True, index=True)
    product_id = fields.Many2one(
        'product.product', domain=[('type', '=', 'service')], string="Product",
        ondelete='restrict', required=True)
