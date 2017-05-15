# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestConditionSimpleFieldSelection(TransactionCase):
    def setUp(self):
        super(TestConditionSimpleFieldSelection, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.date.diff')])
        self.TestModel = self.env[self.test_model.model]

        self.test_field_selection = self.test_model.field_id.filtered(
            lambda r: r.name == 'test_selection')

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

    def _check_selection_condition(self, val1, val2, operator):
        """ Test selection values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_selection.id,
            'condition_simple_field_value_selection': val2,
            'condition_simple_field_selection_operator': operator,
        })
        return condition.check(self._create_record(test_selection=val1))

    def test_10_simple_field_selection(self):
        self.assertTrue(self._check_selection_condition('val1', 'val1', '='))
        self.assertFalse(self._check_selection_condition('val1', 'val2', '='))

        self.assertTrue(self._check_selection_condition('val1', 'val2', '!='))
        self.assertFalse(self._check_selection_condition('val2', 'val2', '!='))

        self.assertTrue(self._check_selection_condition('val1', False, 'set'))
        self.assertFalse(self._check_selection_condition(False, False, 'set'))

        self.assertTrue(
            self._check_selection_condition(False, False, 'not set'))
        self.assertFalse(
            self._check_selection_condition('val2', False, 'not set'))
