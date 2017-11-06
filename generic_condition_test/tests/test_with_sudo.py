# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.exceptions import AccessError
from openerp.tools.misc import mute_logger


class TestConditionRelatedCondition(TransactionCase):

    def _get_model_field(self, model, field):
        return self.env['ir.model.fields'].search([
            ('model_id.model', '=', model),
            ('name', '=', field),
        ])

    def setUp(self):
        super(TestConditionRelatedCondition, self).setUp()
        self.test_model_name = 'test.generic.condition.test.model'
        self.test_model_relation_name = (
            'test.generic.condition.test.model.relation')

        self.test_model = self.env['ir.model'].search(
            [('model', '=', self.test_model_name)])
        self.test_model_relation = self.env['ir.model'].search(
            [('model', '=', self.test_model_relation_name)])

        # Access right, allow only employees to read related model
        self.model_access = self.env.ref(
            'generic_condition_test.'
            'access_test_generic_condition_test_model_relation_any')
        self.model_access.group_id = self.env.ref(
            'base.group_user')

        # Demo-user
        self.demo_user = self.env.ref('base.user_demo')
        self.demo_user.groups_id = self.env.ref(
            'generic_condition_test.group_condition_no_access')
        self.uenv = self.env(user=self.demo_user)

        # Example condition
        # TODO: move this condition definition to demo-data
        self.condition = self.env['generic.condition'].create({
            "name": 'Related conditions condition',
            "model_id": self.test_model.id,
            "type": 'related_conditions',
            "condition_rel_field_id": self._get_model_field(
                self.test_model_name,
                'test_m2o').id,
            "condition_rel_record_operator": 'match',
            "condition_rel_conditions_operator": 'and',
            "condition_rel_conditions": [
                (0, 0, {
                    "name": 'Related field condition',
                    "model_id": self.test_model_relation.id,
                    "type": 'simple_field',
                    'condition_simple_field_field_id': self._get_model_field(
                        self.test_model_relation_name,
                        'name').id,
                    'condition_simple_field_value_char': 'name',
                    'condition_simple_field_string_operator': '=',
                }),
            ]
        })
        self.ucondition = self.condition.sudo(self.demo_user)

        # Record to be checked
        self.rec = self.env.ref(
            'generic_condition_test.test_generic_condition_model_rec')
        self.urec = self.rec.sudo(self.demo_user.id)

    @mute_logger('openerp.addons.generic_condition.models.generic_condition')
    def test_10_related_condition_without_sudo(self):
        with self.assertRaises(AccessError):
            self.ucondition.check(self.urec)

    def test_20_related_condition_with_sudo(self):
        self.condition.with_sudo = True
        self.assertTrue(self.ucondition.check(self.urec))
