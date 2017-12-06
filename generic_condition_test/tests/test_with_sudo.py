# -*- coding: utf-8 -*-
from openerp.tests.common import SavepointCase
from openerp.exceptions import AccessError
from openerp.tools.misc import mute_logger


class TestConditionRelatedCondition(SavepointCase):

    @classmethod
    def _get_model_field(cls, model, field):
        return cls.env['ir.model.fields'].search([
            ('model_id.model', '=', model),
            ('name', '=', field),
        ])

    @classmethod
    def setUpClass(cls):
        super(TestConditionRelatedCondition, cls).setUpClass()
        cls.test_model_name = 'test.generic.condition.test.model'
        cls.test_model_relation_name = (
            'test.generic.condition.test.model.relation')

        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')
        cls.test_model_relation = cls.env.ref(
            'generic_condition_test.'
            'model_test_generic_condition_test_model_relation')

        # Access right, allow only employees to read related model
        cls.model_access = cls.env.ref(
            'generic_condition_test.'
            'access_test_generic_condition_test_model_relation_any')
        cls.model_access.group_id = cls.env.ref(
            'base.group_user')

        # Demo-user
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.demo_user.groups_id = cls.env.ref(
            'generic_condition_test.group_condition_no_access')
        cls.uenv = cls.env(user=cls.demo_user)

        # Example condition
        # TODO: move this condition definition to demo-data
        cls.condition = cls.env['generic.condition'].create({
            "name": 'Related conditions condition',
            "model_id": cls.test_model.id,
            "type": 'related_conditions',
            "condition_rel_field_id": cls._get_model_field(
                cls.test_model_name,
                'test_m2o').id,
            "condition_rel_record_operator": 'match',
            "condition_rel_conditions_operator": 'and',
            "condition_rel_conditions": [
                (0, 0, {
                    "name": 'Related field condition',
                    "model_id": cls.test_model_relation.id,
                    "type": 'simple_field',
                    'condition_simple_field_field_id': cls._get_model_field(
                        cls.test_model_relation_name,
                        'name').id,
                    'condition_simple_field_value_char': 'name',
                    'condition_simple_field_string_operator': '=',
                }),
            ]
        })
        cls.ucondition = cls.condition.sudo(cls.demo_user)

        # Record to be checked
        cls.rec = cls.env.ref(
            'generic_condition_test.test_generic_condition_model_rec')
        cls.urec = cls.rec.sudo(cls.demo_user.id)

    @mute_logger('odoo.addons.generic_condition.models.generic_condition')
    def test_10_related_condition_without_sudo(self):
        with self.assertRaises(AccessError):
            self.ucondition.check(self.urec)

    def test_20_related_condition_with_sudo(self):
        self.condition.with_sudo = True
        self.assertTrue(self.ucondition.check(self.urec))
