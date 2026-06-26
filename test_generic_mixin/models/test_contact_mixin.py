from odoo import fields, models


class TestContactMixin(models.Model):
    _name = 'test.contact.mixin'
    _description = "Test Contact Mixin"

    _inherit = 'generic.mixin.contact'

    name = fields.Char()
