# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
# from openerp.exceptions import AccessError


class TestConditionRelatedCondition(TransactionCase):
    def setUp(self):
        super(TestConditionRelatedCondition, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])
        self.test_model_relation = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model.relation')])

        self.TestModel = self.env[self.test_model.model]
        self.TestRelatedModel = self.env[self.test_model_relation.model]

        self.Condition = self.env['generic.condition']
        self.condition_data = {
            "name": 'Related conditions condition',
            "model_id": self.test_model.id,
            "type": 'related_conditions',
        }

    def _create_condition(self, field, operator, cond_operator, rel_cond):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_data.copy()
        field = self.test_model.field_id.filtered(lambda r: r.name == field)
        condition_data.update({
            "condition_rel_field_id": field.id,
            "condition_rel_record_operator": operator,
            "condition_rel_conditions_operator": cond_operator,
            "condition_rel_conditions": (4, rel_cond)
        })
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def test_10_related_condition_eval_with_sudo(self):

        self.demo_user = self.env.ref(
            'generic_condition_test.user_demo_condition_no_access')
        self.uenv = self.env(user=self.demo_user)

        rel_cond = self.Condition.create({
            "name": 'Related field condition',
            "model_id": self.test_model_relation.id,
            "type": 'simple_field',
            'condition_simple_field_field_id':
                self.test_model_relation.field_id.filtered(
                    lambda r: r.name == 'name').id,
            'condition_simple_field_value_char': 'name',
            'condition_simple_field_string_operator': '=',
        })

        condition = self._create_condition(
            'test_m2o', 'match', 'and', rel_cond.id)

        relation = self.TestRelatedModel.create({
            'name': 'name'
        })

        rec = self._create_record(test_m2o=relation.id)
        rec_u = self.uenv['test.generic.condition.test.model'].browse(rec.id)
        condition_u = self.uenv['generic.condition'].browse(condition.id)
        self.assertTrue(condition.check(rec))
        # self.assertRaises(AccessError, lambda: condition.sudo(
        # self.demo_user.id).check(rec_u))

        condition.write({'with_sudo': True})
        self.assertTrue(condition_u.check(rec_u))
