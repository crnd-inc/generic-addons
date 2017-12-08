from openerp import models, fields


class TestModel(models.Model):
    _name = 'generic.tag.test.model'
    _inherit = [
        'generic.tag.mixin'
    ]

    name = fields.Char()
    test_field = fields.Char('test_field')
