# -*- coding: utf-8 -*-
from openerp import models, fields


class TestConditionModel(models.Model):
    _name = 'test.generic.condition.test.model'

    # date diff fields
    date_start = fields.Datetime()
    date_end = fields.Datetime()
    date_test = fields.Date()

    # simple fields
    test_char = fields.Char()
    test_int = fields.Integer()
    test_float = fields.Float()
    test_selection = fields.Selection([('val1', 'Value 1'),
                                       ('val2', 'Value 2')])
    test_bool = fields.Boolean()

    # Related fields
    test_m2o = fields.Many2one('test.generic.condition.test.model.relation')
    test_m2m = fields.Many2many(
        'test.generic.condition.test.model.relation',
        'test_generic_condition_test_model_relation_rel')


class TestConditionModelRelation(models.Model):
    _name = 'test.generic.condition.test.model.relation'

    name = fields.Char()
