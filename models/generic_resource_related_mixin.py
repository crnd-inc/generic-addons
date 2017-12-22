# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class GenericResourceRelatedMixin(models.AbstractModel):
    """ Simple mixin, that added additional fields to easily select resource
        related to object.


        If you want link to resource, and provide user better UI to select
        related resources, use this mixin.

        It adds additional fields
          - resource_type_id
          - resource_res_model
          - resource_res_id
          - resource_id (computed)

        Use following UI workflow to select relate resource
        1. user selects resource type
        2. user selects object that implements resource (resource_res_id)
           use here generic_m2o widget, to make user able to search records
           in resource model, selected by type (use related resource_res_model)
           field
        4. resource_id will be computed automaticly based on type and res_id

        Example usage in view:

        <field name="resource_type_id"
               options="{'no_create': true, 'no_quick_create': true}"/>
        <field name="resource_res_model" invisible="1"/>
        <field name="resource_res_id" widget="generic_m2o"
               model_field="resource_res_model"
               attrs="{'invisible': [('resource_res_model', '=', False)]}"/>

        If you want to set default resource ID via context, use following
        example:

        context={'default_resource_res_id': res_id,
                 'default_resource_type_id': res_type_id}
    """
    _name = 'generic.resource.related.mixin'

    resource_type_id = fields.Many2one('generic.resource.type',
                                       string='Resource type')
    resource_res_model = fields.Char(
        related="resource_type_id.model_id.model", readonly=True)
    resource_res_id = fields.Integer(string="Resource")
    resource_id = fields.Many2one('generic.resource',
                                  compute='_compute_resource_id',
                                  inverse='_inverse_resource_id',
                                  string='Resource', index=True,
                                  store=True, ondelete='restrict')

    @api.depends('resource_type_id', 'resource_res_id')
    def _compute_resource_id(self):
        for rec in self:
            if rec.resource_type_id and rec.resource_res_id:
                rec.resource_id = self.env[rec.resource_res_model].browse(
                    rec.resource_res_id).resource_id.id
            else:
                rec.resource_id = False

    def _inverse_resource_id(self):
        for rec in self:
            if rec.resource_id:
                rec.write({
                    'resource_type_id': rec.resource_id.res_type_id.id,
                    'resource_res_id': rec.resource_id.res_id,
                })

    @api.constrains('resource_type_id', 'resource_res_id')
    def _constrain_related_resource(self):
        for rec in self:
            if rec.resource_type_id and rec.resource_res_id:
                ResModel = self.env[rec.resource_res_model]
                if not ResModel.browse(rec.resource_res_id).exists():
                    raise ValidationError(_(
                        'Wrong combination of resource type and resource ID!'))
            elif rec.resource_type_id and not rec.resource_res_id:
                raise ValidationError(_(
                    'Resource type specified, but Resource ID not set!'))
            elif rec.resource_res_id and not rec.resource_type_id:
                raise ValidationError(_(
                    'Resource ID specified, but Resource type not set!'))

    @api.onchange('resource_type_id')
    def _onchange_resource_type_id_clean_resource_res_id(self):
        if self.resource_type_id:
            if not self.env[self.resource_type_id.model].browse(
                    self.resource_res_id).exists():
                self.resource_res_id = False
        else:
            self.resource_res_id = False

    @api.model
    def default_get(self, field_names):
        defaults = super(GenericResourceRelatedMixin, self).default_get(
            field_names)

        if ('resource_res_model' in field_names and
                'resource_type_id' in defaults):
            res_type = self.env['generic.resource.type'].browse(
                defaults['resource_type_id']
            )
            defaults['resource_res_model'] = res_type.model_id.model

        return defaults
