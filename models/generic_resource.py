# -*- coding: utf-8 -*-

from openerp import fields, models, api


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

    name = fields.Char(compute="_compute_name", readonly=True)
    code = fields.Char(
        related='interface_id.code', readonly=True, string="interface code",
        store=True, index=True)
    resource_id = fields.Many2one(
        'generic.resource', string="Resource", required=True, index=True)
    interface_id = fields.Many2one(
        'generic.resource.interface', string="Interface", required=True,
        index=True)
    implementation_model = fields.Char(
        related='interface_id.model_id.model', readonly=True, store=True,
        index=True)
    implementation_id = fields.Integer(
        string="Implementation", required=True, index=True)

    @api.depends('implementation_model', 'implementation_id', 'resource_id')
    def _compute_name(self):
        for rec in self:
            if (rec.implementation_model and rec.implementation_id and
                    rec.resource_id):
                impl_name = self.env[rec.implementation_model].browse(
                    rec.implementation_id).display_name
                rec.name = rec.resource_id.display_name + ": " + impl_name


class GenericResourceInterface(models.Model):
    _name = 'generic.resource.interface'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Interface"

    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'interface_id',
        string="Inplementations")
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


class GenericResourceMixin(models.AbstractModel):
    _name = 'generic.resource.mixin'
    _inherits = {'generic.resource': 'resource_id'}

    def _default_resource_id(self):
        return self.env['generic.resource'].create({
            'res_type_id': self._get_resource_type().id,
            'res_id': -1
        })

    resource_id = fields.Many2one(
        'generic.resource', index=True, auto_join=True, ondelete='restrict',
        required=True, default=_default_resource_id)

    _sql_constraints = [
        ('unique_resource_id', 'UNIQUE(resource_id)',
         'Resource must be unique')
    ]

    @api.model
    def write(self, vals):
        # Deny write resource_id field
        if vals.get('resource_id', None):
            del vals['resource_id']

        return super(GenericResourceMixin, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(GenericResourceMixin, self).create(vals)

        # Update res_id with created id
        res.resource_id.update({'res_id': res.id})
        return res

    @api.multi
    def _get_resource_type(self):
        r_type_env = self.env['generic.resource.type']
        model = self.env['ir.model'].search([('name', '=', self._name)])

        r_type = r_type_env.search([('model_id', '=', model.id)])
        if not r_type:
            r_type = r_type_env.create({'model_id': model.id})

        return r_type
