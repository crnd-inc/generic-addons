from odoo import fields, models


class GenericResourceTestModel(models.Model):
    _name = 'generic.resource.test.model'
    _description = 'Generic Resource Test Model'
    _inherit = [
        'generic.resource.mixin',
    ]

    _rec_name = 'name'

    name = fields.Char(index=True, required=True, translate=True)
    active = fields.Boolean(related="resource_id.active", default=True)
