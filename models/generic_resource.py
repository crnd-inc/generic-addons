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
        string="Resource", required=True, index=True, readonly=True)

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
                    record.res_model].browse(record.res_id)
                result.append((record.id, name.display_name))
            else:
                result.append((record.id, False))
        return result

    @api.depends('implementation_ids')
    def _compute_implementation_count(self):
        for rec in self:
            rec.implementation_count = len(rec.implementation_ids)


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
            _logger.warning("Trying write something in the resource_id field")
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

    def unlink(self):
        # Get resources
        resources = self.mapped('resource_id')

        # Delete records
        res = super(GenericResourceMixin, self).unlink()
        # Delete resources and return status
        resources.unlink()
        return res

    def _get_resource_type(self):
        r_type_env = self.env['generic.resource.type']
        return r_type_env.search([('model_id.model', '=', self._name)])
