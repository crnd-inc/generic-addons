from odoo import models, fields


class TestNameSearchByFields(models.Model):
    _name = 'test.mixin.name.search.by.fields'
    _inherit = 'generic.mixin.namesearch.by.fields'
    _description = "Test Generic Mixin: Name Search by Fields"

    _generic_namesearch_fields = ['name', 'code']

    name = fields.Char()
    code = fields.Char()
    test_field = fields.Char()


class TestNameSearchByFields2(models.Model):
    _name = 'test.mixin.name.search.by.fields.2'
    _inherit = 'generic.mixin.namesearch.by.fields'
    _description = "Test Generic Mixin: Name Search by Fields 2"

    _generic_namesearch_fields = ['code']
    _generic_namesearch_search_by_rec_name = True

    name = fields.Char()
    code = fields.Char()
    test_field = fields.Char()
