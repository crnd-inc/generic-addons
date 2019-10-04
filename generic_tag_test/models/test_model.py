from odoo import models, fields


class TestModel(models.Model):
    _name = 'generic.tag.test.model'
    _inherit = [
        'generic.tag.mixin'
    ]
    _description = "Generic Tag Test Model"

    name = fields.Char()
    test_field = fields.Char('test_field')
