from odoo.tests.common import (tagged, TransactionCase)


@tagged('-at_install', 'post_install')
class TestConditionAutomation(TransactionCase):

    def test_condition_automation(self):
        partner = self.env.ref('generic_condition.demo_partner_z_corp')

        self.assertFalse(partner.user_id)
        self.assertEqual(partner.city, 'Kyiv')

        partner.write({'city': 'New York'})

        self.assertNotEqual(partner.city, 'Kyiv')

    def test_condition_automation_onchange_model_id(self):
        rule = self.env.ref('generic_condition_automation.test_rule_on_write')
        self.assertTrue(rule.pre_condition_ids)
        self.assertTrue(rule.post_condition_ids)
        self.assertEqual(rule.trigger, 'on_write')

        rule._onchange_model_id()

        self.assertFalse(rule.pre_condition_ids)
        self.assertFalse(rule.post_condition_ids)

    def test_condition_automation_onchange_trigger(self):
        rule = self.env.ref('generic_condition_automation.test_rule_on_write')
        self.assertTrue(rule.pre_condition_ids)
        self.assertTrue(rule.post_condition_ids)
        self.assertEqual(rule.trigger, 'on_write')

        rule.trigger = 'on_create'
        rule._onchange_trigger()

        self.assertFalse(rule.pre_condition_ids)
