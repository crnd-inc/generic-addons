# -*- coding: utf-8 -*-

from openerp import fields, models, api


class GenericResourceInterface(models.Model):
    _name = 'generic.resource.interface'
    _inherits = {'ir.model': 'model_id'}
    _description = "Generic Resource Interface"

    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'resource_interface_id',
        string="Implementations")
    implementation_count = fields.Integer(
        compute="_compute_implementation_count")
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


class GenericResourceInterfaceMixin(models.AbstractModel):
    """ Use this mixin if you want to add interface implementation
        bechavior to your model.

        Note, your model name must be less than 32 symbols, to make it work.
        Reason for this, is three level inehritance:
         Your Model -> generic.resource.implementation -> generic.resource
        And thus, to access resource fields from your model, odoo builds
        table aliaces like:
           your_model__implementation_id__resource_id
        Max postgres tablename len is 64 characters,
        len('__implementation_id__resource_id') is 32
    """
    _name = 'generic.resource.interface.mixin'

    implementation_id = fields.Many2one(
        'generic.resource.implementation', index=True, required=True,
        auto_join=True, ondelete='restrict', delegate=True,
        old_name='resource_implementation_id')

    @api.model
    def create(self, vals):
        # Add vals for implementation with fake id
        vals['resource_interface_id'] = self._get_resource_interface().id
        vals['resource_impl_id'] = -1

        res = super(GenericResourceInterfaceMixin, self).create(vals)

        # Update resource_impl_id with created id
        res.implementation_id.update({
            'resource_impl_id': res.id})
        return res

    def _get_resource_interface(self):
        interface_env = self.env['generic.resource.interface']
        return interface_env.search([('model_id.model', '=', self._name)])
