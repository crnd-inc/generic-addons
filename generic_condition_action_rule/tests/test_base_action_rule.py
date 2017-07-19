# -*- coding: utf-8 -*-
from openerp.tests.common import (at_install,
                                  post_install,
                                  TransactionCase)


@at_install(False)
@post_install(True)
class TestBaseActionRuleCondition(TransactionCase):

    def test_action_rule(self):
        demo_user = self.env.ref('base.user_demo')
        partner = self.env.ref('generic_condition.demo_partner_z_corp')

        self.assertFalse(partner.user_id)
        self.assertEqual(partner.city, 'Kyiv')

        partner.write({'city': 'New York'})

        self.assertNotEqual(partner.city, 'Kyiv')

        self.assertEqual(partner.user_id, demo_user)

    def test_action_rule_onchange_kind(self):
        rule = self.env.ref('generic_condition_action_rule.test_rule_on_write')
        self.assertTrue(rule.pre_condition_ids)
        self.assertTrue(rule.post_condition_ids)
        self.assertEqual(rule.kind, 'on_write')

        rule.kind = 'on_create'

        rule.onchange_kind()

        self.assertFalse(rule.pre_condition_ids)

    def test_action_rule_onchange_model_id(self):
        rule = self.env.ref('generic_condition_action_rule.test_rule_on_write')
        self.assertTrue(rule.pre_condition_ids)
        self.assertTrue(rule.post_condition_ids)
        self.assertEqual(rule.kind, 'on_write')

        rule.model_id = self.env.ref('base.model_res_country')

        rule.onchange_model_id()

        self.assertFalse(rule.pre_condition_ids)
        self.assertFalse(rule.post_condition_ids)
