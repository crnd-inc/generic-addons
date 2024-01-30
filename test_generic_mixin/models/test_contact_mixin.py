from odoo import fields, models


class TestContactMixin(models.Model):
    _name = 'test.contact.mixin'

    _inherit = 'generic.mixin.contact'

    name = fields.Char()
