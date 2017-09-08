# -*- coding: utf-8 -*-

from openerp import fields, models, api


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

    _sql_constraints = [
        ('model_id_uniq',
         'UNIQUE (model_id)',
         'For each Odoo model only one Resource Type can be created!'),
    ]

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for rec in self:
            rec.resource_count = len(rec.resource_ids)

    @api.onchange('model_id')
    def _onchenge_model_id(self):
        for rec in self:
            if rec.model_id:
                rec.name = rec.model_id.name
