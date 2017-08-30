# -*- coding: utf-8 -*-

from openerp import fields, models, api


import logging
_logger = logging.getLogger(__name__)


class GenericResource(models.Model):
    _name = 'generic.resource'
    _description = 'Generic Resource'

    active = fields.Boolean(default=True, index=True)
    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'resource_id',
        string="Implementations")
    implementation_count = fields.Integer(
        compute="_compute_implementation_count")
    res_type_id = fields.Many2one(
        'generic.resource.type', string="Type", required=True, index=True)
    res_model = fields.Char(
        related='res_type_id.model_id.model', readonly=True, store=True,
        index=True)
    res_id = fields.Integer(
        string="Model", required=True, index=True, readonly=True)

    _sql_constraints = [
        ('unique_model', 'UNIQUE(res_model, res_id)',
         'Model instance must be unique')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.res_model and record.res_id:
                name = self.env[
                    record.res_model].browse(record.res_id).display_name
                result.append((record.id, name))
            else:
                result.append((record.id, False))
        return result

    @api.depends('implementation_ids')
    def _compute_implementation_count(self):
        for rec in self:
            rec.implementation_count = len(rec.implementation_ids)


class GenericResourceImplementation(models.Model):
    _name = 'generic.resource.implementation'
    _description = 'Generic Resource Implementation'

    resource_id = fields.Many2one(
        'generic.resource', string="Resource", required=True, index=True)
    resource_interface_id = fields.Many2one(
        'generic.resource.interface', string="Interface", required=True,
        index=True)
    resource_impl_model = fields.Char(
        related='resource_interface_id.model_id.model', readonly=True,
        store=True, index=True)
    resource_impl_id = fields.Integer(
        string="Implementation", required=True, index=True)

    _sql_constraints = [
        ('unique_model', 'UNIQUE(resource_id, resource_interface_id)',
         'Resource and interface must be unique in implementation')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if (record.resource_impl_model and record.resource_impl_id and
                    record.resource_id):
                impl_name = self.env[record.resource_impl_model].browse(
                    record.resource_impl_id).display_name
                name = record.resource_id.display_name + ": " + impl_name
                result.append((record.id, name))
            else:
                result.append((record.id, False))
        return result


class GenericResourceInterface(models.Model):
    _name = 'generic.resource.interface'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Interface"

    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'resource_interface_id',
        string="Implementations")
    implementation_count = fields.Integer(
        compute="_compute_implementation_count",
        string="Inplementation count")
    resource_count = fields.Integer(
        compute="_compute_resource_count")
    code = fields.Char(index=True, required=True)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        ondelete='restrict')

    @api.depends('implementation_ids')
    def _compute_implementation_count(self):
        for rec in self:
            rec.implementation_count = len(rec.implementation_ids)

    @api.depends('implementation_ids.resource_id')
    def _compute_resource_count(self):
        for rec in self:
            rec.resource_count = len(
                rec.implementation_ids.mapped('resource_id'))


class GenericResourceType(models.Model):
    _name = 'generic.resource.type'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Type"

    name = fields.Char(index=True, required=True, translate=True)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        ondelete='restrict')
    resource_ids = fields.One2many(
        'generic.resource', 'res_type_id', string='Resources')
    resource_count = fields.Integer(compute="_compute_resource_count")

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for rec in self:
            rec.resource_count = len(rec.resource_ids)

    @api.onchange('model_id')
    def _onchenge_model_id(self):
        for rec in self:
            if rec.model_id:
                rec.name = rec.model_id.name


class GenericResourceMixin(models.AbstractModel):
    _name = 'generic.resource.mixin'
    _inherits = {'generic.resource': 'resource_id'}

    resource_id = fields.Many2one(
        'generic.resource', index=True, auto_join=True, ondelete='restrict',
        required=True)

    _sql_constraints = [
        ('unique_resource_id', 'UNIQUE(resource_id)',
         'Resource must be unique')
    ]

    @api.multi
    def write(self, vals):
        # Deny write resource_id field
        if vals.get('resource_id', None):
            _logger.warn("Trying write something in the resource_id field")
            del vals['resource_id']

        return super(GenericResourceMixin, self).write(vals)

    @api.model
    def create(self, vals):
        # Add vals for resource with fake id
        vals['res_type_id'] = self._get_resource_type().id
        vals['res_id'] = -1

        res = super(GenericResourceMixin, self).create(vals)

        # Update res_id with created id
        res.resource_id.update({'res_id': res.id})
        return res

    def _get_resource_type(self):
        r_type_env = self.env['generic.resource.type']
        return r_type_env.search([('model_id.model', '=', self._name)])


class GenericResourceInterfaceMixin(models.Model):
    _name = 'generic.resource.interface.mixin'
    _inherits = {
        'generic.resource.implementation': 'resource_implementation_id'}

    resource_implementation_id = fields.Many2one(
        'generic.resource.implementation', index=True, required=True,
        auto_join=True, ondelete='restrict')

    @api.model
    def create(self, vals):
        # Add vals for implementation with fake id
        vals['resource_interface_id'] = self._get_resource_interface().id
        vals['resource_impl_id'] = -1

        res = super(GenericResourceInterfaceMixin, self).create(vals)

        # Update resource_impl_id with created id
        res.resource_implementation_id.update({
            'resource_impl_id': res.id})
        return res

    def _get_resource_interface(self):
        interface_env = self.env['generic.resource.interface']
        return interface_env.search([('model_id.model', '=', self._name)])
