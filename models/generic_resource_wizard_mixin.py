from odoo import api, models, fields, exceptions, _


class ResourceWizardMixin(models.AbstractModel):
    """ Simple mixin for mass action wizards for resources

        Allows to automatically detect list of resources from context
    """
    _name = 'generic.resource.wizard.mixin'
    _description = 'Resource Wizard: Mixin'

    resource_type_id = fields.Many2one(
        'generic.resource.type',
        compute='_compute_resource_type_id',
        readonly=True)
    resource_ids = fields.Many2many(
        'generic.resource')

    @api.depends('resource_ids', 'resource_ids.res_type_id')
    def _compute_resource_type_id(self):
        for record in self:
            rt = record.resource_ids.mapped('res_type_id')
            if len(rt) == 1:
                record.resource_type_id = rt
            else:
                record.resource_type_id = False

    @api.constrains('resource_ids')
    def _check_resource_type_and_resources(self):
        for record in self:
            rt = record.resource_ids.mapped('res_type_id')
            if len(rt) != 1:
                raise exceptions.ValidationError(_(
                    "Cannot apply this action to resources "
                    "with different types! "
                    "Please, select resources of single resource type"))

    @api.model
    def default_get(self, fields_list):
        res = super(ResourceWizardMixin, self).default_get(fields_list)

        active_model = self.env.context.get('active_model')
        if not active_model:
            return res

        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            active_id = self.env.context.get('active_id')
            active_ids = [active_id] if active_id else active_ids
        if not active_ids:
            return res

        if active_model == 'generic.resource':
            res['resource_ids'] = [(6, 0, active_ids)]
        elif self.env['generic.resource.type'].get_resource_type(active_model):
            res['resource_ids'] = [
                (6, 0, self.env[active_model].browse(
                    active_ids).mapped('resource_id').ids)
            ]
        return res
