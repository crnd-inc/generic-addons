# -*- coding: utf-8 -*-

from openerp import fields, models, api


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
