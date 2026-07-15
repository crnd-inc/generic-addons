from odoo.tests.common import (tagged, TransactionCase)


@tagged('-at_install', 'post_install')
class TestConditionAutomation(TransactionCase):

    def tearDown(self):
        self.env['base.automation']._unregister_hook()
        super().tearDown()

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

    def test_condition_automation_write_as_non_admin(self):
        # A plain internal user (without Settings/Administration access) has no
        # read access to 'base.automation'. When such a user writes to a record
        # that triggers an automation with pre/post generic conditions, the
        # _filter_pre / _filter_post overrides must access the condition fields
        # in sudo -- otherwise reading pre_condition_ids/post_condition_ids on
        # the automation (bound to the user's env by base_automation) raises
        # AccessError. This test reproduces that scenario.
        rule = self.env.ref('generic_condition_automation.test_rule_on_write')
        self.assertEqual(rule.trigger, 'on_write')

        user = self.env['res.users'].create({
            'name': 'Generic Condition Automation Test User',
            'login': 'generic_condition_automation_test_user',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                # allow writing to res.partner, but *not* to base.automation
                self.env.ref('base.group_partner_manager').id,
            ])],
        })
        # sanity check: the user really has no access to automation rules
        self.assertFalse(
            user.has_group('base.group_system'),
            "Test user must not be an administrator",
        )

        partner = self.env.ref('generic_condition.demo_partner_z_corp')
        self.assertEqual(partner.city, 'Kyiv')

        # Drop everything from the transaction cache so the automation's
        # pre/post condition fields are actually fetched during the write,
        # reproducing the cold-cache production scenario.
        # Without this, an earlier su read of those fields would populate
        # the shared cache and mask the AccessError.
        self.env.invalidate_all()

        # Must not raise AccessError on 'base.automation'.
        partner.with_user(user).write({'city': 'New York'})

        self.assertEqual(partner.city, 'New York')
