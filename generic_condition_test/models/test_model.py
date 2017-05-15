# -*- coding: utf-8 -*-
from openerp import models, fields


class TestConditionDateDiff(models.Model):
    _name = 'test.generic.condition.date.diff'

    date_start = fields.Datetime()
    date_end = fields.Datetime()

    date_test = fields.Date()

    test_char = fields.Char()
    test_int = fields.Integer()
    test_float = fields.Float()
    test_selection = fields.Selection([('val1', 'Value 1'),
                                       ('val2', 'Value 2')])
    test_bool = fields.Boolean()
