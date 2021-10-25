from odoo import fields, models


class GenericResourcePermission(models.Model):
    _name = 'generic.resource.permission'

    _description = 'Generic Resource Permission'

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()
    res_type_id = fields.Many2one(
        'generic.resource.type', string="Resource Type",
        required=True, index=True, ondelete='cascade')
