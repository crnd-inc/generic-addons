# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class GenericResourceImplementation(models.Model):
    """ Implementation of resource interface

        This model is inehrited from `generic.resource` so, all fields
        of `generic.resource` should be available here
    """
    _name = 'generic.resource.implementation'
    _description = 'Generic Resource Implementation'

    resource_id = fields.Many2one(
        'generic.resource', string="Resource", required=True, index=True,
        auto_join=True, ondelete='restrict', delegate=True)
    resource_interface_id = fields.Many2one(
        'generic.resource.interface', string="Interface", required=True,
        index=True, ondelete='restrict')
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
                # This case, when implementation model is not present in pool,
                # may happen, when addon that implements resource
                # implementationwas was uninstalled.
                # TODO: handle this in better way
                try:
                    ImplModel = self.env[record.resource_impl_model]
                except KeyError:
                    impl_name = _("Error: no model")
                else:
                    impl_name = ImplModel.browse(
                        record.resource_impl_id
                    ).display_name

                name = u"%s: %s" % (record.resource_id.display_name, impl_name)
                result.append((record.id, name))
            else:
                result.append((record.id, False))
        return result
