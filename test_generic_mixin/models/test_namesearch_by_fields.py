from odoo import models, fields


class TestNameSearchByFields(models.Model):
    _name = 'test.mixin.name.search.by.fields'
    _inherit = 'generic.mixin.namesearch.by.fields'

    _generic_namesearch_fields = ['name', 'code']

    name = fields.Char()
    code = fields.Char()
    test_field = fields.Char()
