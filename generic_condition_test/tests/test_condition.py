# -*- coding: utf-8 -*-
from openerp.tools.misc import mute_logger
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestConditionDateDiff(TransactionCase):
    """ This test case requires creation of separate model with at least
        two date / datetime fields, so it is implemented as separate test case
        in separate addon.
    """

    def setUp(self):
        super(TestConditionDateDiff, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.date.diff')])
        self.TestModel = self.env[self.test_model.model]
        self.test_field_start_date = self.test_model.field_id.filtered(
            lambda r: r.name == 'date_start')
        self.test_field_end_date = self.test_model.field_id.filtered(
            lambda r: r.name == 'date_end')
        self.test_field_test_date = self.test_model.field_id.filtered(
            lambda r: r.name == 'date_test')

        self.Condition = self.env['generic.condition']
        self.condition_date_diff = self.Condition.create({
            "name": 'Date diff test',
            "model_id": self.test_model.id,
            "type": 'date_diff',
            "condition_date_diff_date_field_start": self.test_field_start_date.id,
            "condition_date_diff_date_field_end": self.test_field_end_date.id,
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
        })

    def test_10_condition_date_diff(self):
        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })
        self.assertFalse(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '!='
        self.assertTrue(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '='
        rec.date_end = '2017-05-03'
        self.assertTrue(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '>'
        self.assertFalse(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '<'
        self.assertFalse(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '<='
        self.assertTrue(self.condition_date_diff.check(rec))

        self.condition_date_diff.condition_date_diff_operator = '>='
        self.assertTrue(self.condition_date_diff.check(rec))

        # test date-diff with different field types (datetime and date)
        rec.date_test = '2017-05-03'
        self.condition_date_diff.write({
            'condition_date_diff_operator': '=',
            'condition_date_diff_date_field_end': self.test_field_test_date.id,
        })
        self.assertTrue(self.condition_date_diff.check(rec))
