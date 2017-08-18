# -*- coding: utf-8 -*-

from openerp import fields, models


class GenericResource(models.Model):
    _name = 'generic.resource'
    _rec_name = 'name'

    name = fields.Char()
    active = fields.Boolean(default=True)
    implementation_ids = fields.One2many('generic.resource.implementation',
                                         'resource_id')


class GenericResourceImplementation(models.Model):
    _name = 'generic.resource.implementation'

    name = fields.Char(related='interface_id.name', readonly=True)
    code = fields.Char(related='interface_id.code', readonly=True)
    resource_id = fields.Many2one('generic.resource')
    interface_id = fields.Many2one('generic.resource.interface')
    implementation_model = fields.Many2one('ir.model',
                                           related='interface_id.model_id',
                                           readonly=True)
    implementation_id = fields.Integer()


class GenericResourceInterface(models.Model):
    _name = 'generic.resource.interface'

    name = fields.Char()
    code = fields.Char()
    model_id = fields.Many2one('ir.model', string="Model")
