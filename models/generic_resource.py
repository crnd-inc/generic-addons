# -*- coding: utf-8 -*-

from openerp import fields, models


class GenericResource(models.Model):
    _name = 'generic.resource'
    _rec_name = 'name'
    _description = 'Generic Resource'

    name = fields.Char()
    active = fields.Boolean(default=True)
    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'resource_id',
        string="Implementations")
    res_type_id = fields.Many2one('generic.resource.type', string="Type")
    res_model = fields.Char(
        related='res_type_id.model_id.model', readonly=True)
    res_id = fields.Integer(string="Model")


class GenericResourceImplementation(models.Model):
    _name = 'generic.resource.implementation'
    _description = 'Generic Resource Implementation'

    name = fields.Char()
    code = fields.Char(
        related='interface_id.code', readonly=True, string="interface code")
    resource_id = fields.Many2one('generic.resource', string="Resource")
    interface_id = fields.Many2one(
        'generic.resource.interface', string="Interface")
    implementation_model = fields.Char(
        related='interface_id.model_id.model', readonly=True)
    implementation_id = fields.Integer(string="Implementation")


class GenericResourceInterface(models.Model):
    _name = 'generic.resource.interface'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Interface"

    code = fields.Char()
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        ondelete='restrict')


class GenericResourceType(models.Model):
    _name = 'generic.resource.type'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Type"

    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        ondelete='restrict')
    resource_ids = fields.One2many(
        'generic.resource', 'res_type_id', string='Resources')
