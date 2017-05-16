# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestConditionSimpleFieldString(TransactionCase):
    def setUp(self):
        super(TestConditionSimpleFieldString, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])
        self.TestModel = self.env[self.test_model.model]

        self.test_field_char = self.test_model.field_id.filtered(
            lambda r: r.name == 'test_char')

        self.Condition = self.env['generic.condition']
        self.condition_data = {
            "name": 'Simple field condition',
            "model_id": self.test_model.id,
            "type": 'simple_field',
        }

    def _create_condition(self, data):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_data.copy()
        condition_data.update(data)
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def _check_string_condition(self, val1, val2, operator,
                                icase=False, regex=False):
        """ Test selection values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_char.id,
            'condition_simple_field_value_char': val2,
            'condition_simple_field_string_operator': operator,
            'condition_simple_field_string_operator_icase': icase,
            'condition_simple_field_string_operator_regex': regex,
        })
        return condition.check(self._create_record(test_char=val1))

    def test_10_condition_simple_field_string_simple(self):
        self.assertTrue(self._check_string_condition('val1', False, 'set'))
        self.assertFalse(self._check_string_condition(False, False, 'set'))

        self.assertTrue(self._check_string_condition(False, False, 'not set'))
        self.assertFalse(
            self._check_string_condition('val1', False, 'not set'))

        self.assertTrue(self._check_string_condition('val1', 'val1', '='))
        self.assertFalse(self._check_string_condition('val123', 'val1', '='))
        self.assertFalse(self._check_string_condition('val1', 'VaL1', '='))
        self.assertFalse(self._check_string_condition('val1', 'val2', '='))
        self.assertFalse(self._check_string_condition(False, 'val2', '='))

        self.assertFalse(self._check_string_condition('val1', 'val1', '!='))
        self.assertTrue(self._check_string_condition('val123', 'val1', '!='))
        self.assertTrue(self._check_string_condition('val1', 'VaL1', '!='))
        self.assertTrue(self._check_string_condition('val1', 'val2', '!='))
        self.assertTrue(self._check_string_condition(False, 'val2', '!='))

        self.assertTrue(
            self._check_string_condition('val1', 'val1', 'contains'))
        self.assertTrue(
            self._check_string_condition('val123', 'val1', 'contains'))
        self.assertFalse(
            self._check_string_condition('val1', 'VaL1', 'contains'))
        self.assertFalse(
            self._check_string_condition('val1', 'val2', 'contains'))
        self.assertFalse(
            self._check_string_condition(False, 'val2', 'contains'))

    def test_20_condition_simple_field_string_simple_icase(self):
        self.assertTrue(
            self._check_string_condition('val1', 'val1', '=', icase=True))
        self.assertFalse(
            self._check_string_condition('val123', 'val1', '=', icase=True))
        self.assertTrue(
            self._check_string_condition('val1', 'VaL1', '=', icase=True))
        self.assertFalse(
            self._check_string_condition('val1', 'val2', '=', icase=True))
        self.assertFalse(
            self._check_string_condition(False, 'val2', '=', icase=True))

        self.assertFalse(
            self._check_string_condition('val1', 'val1', '!=', icase=True))
        self.assertTrue(
            self._check_string_condition('val123', 'val1', '!=', icase=True))
        self.assertFalse(
            self._check_string_condition('val1', 'VaL1', '!=', icase=True))
        self.assertTrue(
            self._check_string_condition('val1', 'val2', '!=', icase=True))
        self.assertTrue(
            self._check_string_condition(False, 'val2', '!=', icase=True))

        self.assertTrue(
            self._check_string_condition(
                'val1', 'val1', 'contains', icase=True))
        self.assertTrue(
            self._check_string_condition(
                'val123', 'val1', 'contains', icase=True))
        self.assertTrue(
            self._check_string_condition(
                'val1', 'VaL1', 'contains', icase=True))
        self.assertFalse(
            self._check_string_condition(
                'val1', 'val2', 'contains', icase=True))
        self.assertFalse(
            self._check_string_condition(
                False, 'val2', 'contains', icase=True))

    def test_30_condition_simple_field_string_simple_regex(self):
        self.assertTrue(
            self._check_string_condition('val1', 'val1', '=', regex=True))
        self.assertTrue(
            self._check_string_condition('val123', 'val1', '=', regex=True))
        self.assertFalse(
            self._check_string_condition('val1', 'VaL1', '=', regex=True))
        self.assertFalse(
            self._check_string_condition('val1', 'val2', '=', regex=True))
        self.assertFalse(
            self._check_string_condition(False, 'val2', '=', regex=True))
        self.assertTrue(
            self._check_string_condition('val1', r'v\w\w\d', '=', regex=True))

        self.assertFalse(
            self._check_string_condition('val1', 'val1', '!=', regex=True))
        self.assertFalse(
            self._check_string_condition('val123', 'val1', '!=', regex=True))
        self.assertTrue(
            self._check_string_condition('val1', 'VaL1', '!=', regex=True))
        self.assertTrue(
            self._check_string_condition('val1', 'val2', '!=', regex=True))
        self.assertTrue(
            self._check_string_condition(False, 'val2', '!=', regex=True))
        self.assertFalse(
            self._check_string_condition('val1', r'v\w\w\d', '!=', regex=True))

        self.assertTrue(self._check_string_condition(
            'val1', 'val1', 'contains', regex=True))
        self.assertTrue(self._check_string_condition(
            'val123', 'val1', 'contains', regex=True))
        self.assertFalse(self._check_string_condition(
            'val1', 'VaL1', 'contains', regex=True))
        self.assertFalse(self._check_string_condition(
            'val1', 'val2', 'contains', regex=True))
        self.assertFalse(self._check_string_condition(
            False, 'val2', 'contains', regex=True))
        self.assertTrue(self._check_string_condition(
            'val1', r'v\w\w\d', 'contains', regex=True))
        self.assertTrue(self._check_string_condition(
            '1223 23 val1 22', r'v\w\w\d', 'contains', regex=True))

    def test_40_condition_simple_field_string_simple_regex_icase(self):
        self.assertTrue(self._check_string_condition(
            'val1', 'val1', '=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val123', 'val1', '=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val1', 'VaL1', '=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'val1', 'val2', '=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            False, 'val2', '=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val1', r'v\w\w\d', '=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'VAl1', r'v\w\w\d', '=', regex=True, icase=True))

        self.assertFalse(self._check_string_condition(
            'val1', 'val1', '!=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'val123', 'val1', '!=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'val1', 'VaL1', '!=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val1', 'val2', '!=', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            False, 'val2', '!=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'val1', r'v\w\w\d', '!=', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'VAl1', r'v\w\w\d', '!=', regex=True, icase=True))

        self.assertTrue(self._check_string_condition(
            'val1', 'val1', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val123', 'val1', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val1', 'VaL1', 'contains', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            'val1', 'val2', 'contains', regex=True, icase=True))
        self.assertFalse(self._check_string_condition(
            False, 'val2', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'val1', r'v\w\w\d', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            '1223 23 val1 22', r'v\w\w\d', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            'VAl1', r'v\w\w\d', 'contains', regex=True, icase=True))
        self.assertTrue(self._check_string_condition(
            '1223 23 VAl1 22', r'v\w\w\d', 'contains', regex=True, icase=True))
