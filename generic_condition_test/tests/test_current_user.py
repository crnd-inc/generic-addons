# -*- coding: utf-8 -*-
from openerp.tests.common import SavepointCase


class TestConditionCurrentUser(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionCurrentUser, cls).setUpClass()
        cls.test_model = cls.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])

        cls.TestModel = cls.env[cls.test_model.model]
        cls.ResUsers = cls.env['res.users']

        cls.Condition = cls.env['generic.condition']
        cls.condition_data = {
            "name": 'Current user condition',
            "model_id": cls.test_model.id,
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
        rec = self._create_record(user_m2o=self.env.user.id)
        self.assertTrue(condition.check(rec))

    def test_15_current_user_m2m(self):
        condition = self._create_condition('user_m2m')

        rec = self._create_record(user_m2m=False)
        self.assertFalse(condition.check(rec))

        users = [self.env.user.id, self.env.ref('base.user_demo').id]

        rec = self._create_record(
            user_m2m=[(6, 0, users)])
        self.assertTrue(condition.check(rec))
