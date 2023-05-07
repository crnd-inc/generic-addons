from odoo import fields, models


class GenericResourceSimple(models.Model):
    _name = 'generic.resource.simple'
    _description = 'Generic Resource Simple'
    _inherit = [
        'mail.thread',
        'generic.resource.mixin',
        'generic.resource.mixin.inv.number',
        'generic.mixin.get.action',
    ]

    _rec_name = 'name'
    _inv_number_seq_code = 'generic.resource.simple.sequence'
    _inv_number_in_display_name = True

    name = fields.Char(index=True, required=True, translate=True)
    active = fields.Boolean(related="resource_id.active")
    category_id = fields.Many2one(
        'generic.resource.simple.category',
        'Category', index=True, ondelete='restrict')
