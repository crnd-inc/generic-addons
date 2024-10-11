from odoo import fields, models, api, _, exceptions


class GenericResourceRelatedMixin(models.AbstractModel):
    """ Simple mixin, that added additional fields to easily select resource
        related to object.


        If you want link to resource, and provide user better UI to select
        related resources, use this mixin.

        It adds additional fields
          - resource_type_id (computed)
          - resource_res_model (related)
          - resource_res_id (computed)
          - resource_id

        Use following UI workflow to select relate resource
        1. user selects resource type
        2. user selects object that implements resource (resource_res_id)
        4. resource_id will be computed automaticly based on type and res_id

        Example usage in view:

        <field name="resource_type_id"
               options="{'no_create': true, 'no_quick_create': true}"/>
        <field name="resource_res_model" invisible="1"/>
        <field name="resource_res_id"
               attrs="{'invisible': [('resource_res_model', '=', False)]}"/>

        If you want to set default resource ID via context, use following
        example:

        context={'default_resource_res_id': res_id,
                 'default_resource_type_id': res_type_id}
    """
    _name = 'generic.resource.related.mixin'
    _description = 'Generic Resource Mixin: Related Resource'

    resource_type_id = fields.Many2one(
        'generic.resource.type', string='Resource type',
        compute="_compute_resource_res_fields", store=True,
        inverse="_inverse_resource_res_id", compute_sudo=True)
    resource_res_model = fields.Char(
        related="resource_type_id.model_id.model",
        string="Resource model", readonly=True)
    resource_res_id = fields.Many2oneReference(
        string="Resource",
        model_field='resource_res_model', store=True,
        compute="_compute_resource_res_fields",
        inverse="_inverse_resource_res_id", compute_sudo=True)
    resource_id = fields.Many2one(
        'generic.resource', string='Generic resource', index=True,
        store=True, ondelete='restrict')

    @api.depends('resource_id', 'resource_id.res_id',
                 'resource_id.res_type_id')
    def _compute_resource_res_fields(self):
        for rec in self.exists():
            if rec.resource_id:
                rec.update({
                    'resource_res_id': rec.resource_id.res_id,
                    'resource_type_id': rec.resource_id.res_type_id.id,
                })
            else:
                rec.update({
                    'resource_res_id': False,
                    'resource_type_id': False,
                })

    def _inverse_resource_res_id(self):
        for rec in self:
            if (rec.resource_res_id and
                    rec.resource_type_id and
                    rec.resource_res_id != -1):
                resource_model = rec.resource_type_id.sudo().model
                resource = self.env[resource_model].browse(
                    rec.resource_res_id)
                if resource.exists():
                    rec.resource_id = resource.resource_id
                else:
                    raise exceptions.ValidationError(_(
                        'Resource does not exists!\n'
                        '\tResource type: %(res_type)s\n'
                        '\tResource res_id: %(res_id)s'
                    ) % {
                        'res_type': rec.resource_type_id.display_name,
                        'res_id': rec.resource_res_id,
                    })
            elif (not rec.resource_type_id and not
                  rec.resource_res_id):
                rec.resource_id = False
            else:
                raise exceptions.ValidationError(_(
                    'Fields incorrect\n'
                    '\tResource type: %(res_type)s\n'
                    '\tResource res_id: %(res_id)s'
                ) % {
                    'res_type': rec.resource_type_id.display_name,
                    'res_id': rec.resource_res_id,
                })

    @api.onchange('resource_type_id')
    def _onchange_resource_type_id_clean_resource_res_id(self):
        if self.resource_type_id:
            resource_model = self.resource_type_id.sudo().model
            if not self.env[resource_model].browse(
                    self.resource_res_id).exists():
                self.resource_res_id = False
        else:
            self.resource_res_id = False

    @api.model
    def default_get(self, field_names):
        defaults = super(GenericResourceRelatedMixin, self).default_get(
            field_names)

        # TODO: Check if this is realy required
        if ('resource_res_model' in field_names and
                'resource_type_id' in defaults):
            res_type = self.env['generic.resource.type'].browse(
                defaults['resource_type_id']
            )
            defaults['resource_res_model'] = res_type.model_id.model

        return defaults
