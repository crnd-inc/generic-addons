# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestConditionCurrentUser(TransactionCase):
    def setUp(self):
        super(TestConditionCurrentUser, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])

        self.TestModel = self.env[self.test_model.model]
        self.ResUsers = self.env['res.users']

        self.Condition = self.env['generic.condition']
        self.condition_data = {
            "name": 'Current user condition',
            "model_id": self.test_model.id,
            "type": 'current_user',
        }

    def _create_condition(self, field_name):
        """ Simple helper to create new condition with some predefined values
        """
        field = self.test_model.field_id.filtered(
            lambda r: r.name == field_name)

        condition_data = self.condition_data.copy()
        condition_data.update({
            'condition_user_user_field_id': field.id,
        })
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def test_10_current_user_m2o(self):
        condition = self._create_condition('user_m2o')

        rec = self._create_record(user_m2o=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(test_m2o=self.env.user.id)
        self.assertTrue(condition.check(rec))

    def test_15_current_user_m2m(self):
        condition = self._create_condition('user_m2m')

        rec = self._create_record(user_m2m=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(
            user_m2m=[(4, self.env.user.id, 0)])
        self.assertTrue(condition.check(rec))
