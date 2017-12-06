# -*- coding: utf-8 -*-
from openerp.tools.misc import mute_logger
from openerp.tests.common import SavepointCase
from openerp.tools.translate import _
from openerp.exceptions import ValidationError


class TestCondition(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCondition, cls).setUpClass()
        cls.Condition = cls.env['generic.condition']

        # demo_data
        cls.partner_demo = cls.env.ref('base.partner_demo')
        cls.partner_sx_corp = cls.env.ref(
            'generic_condition.demo_partner_sx_corp')
        cls.partner_z_corp = cls.env.ref(
            'generic_condition.demo_partner_z_corp')

        # demo conditions
        cls.condition_eval_error = cls.env.ref(
            'generic_condition.demo_condition_eval_error')
        cls.condition_partner_sx_corp = cls.env.ref(
            'generic_condition.demo_condition_partner_sx_corp')
        cls.condition_partner_not_sx_corp = cls.env.ref(
            'generic_condition.demo_condition_partner_not_sx_corp')
        cls.condition_partner_city_kyiv = cls.env.ref(
            'generic_condition.demo_condition_partner_city_kyiv')
        cls.condition_partner_not_sx_corp_but_kyiv = cls.env.ref(
            'generic_condition.demo_condition_partner_not_sx_corp_but_kyiv')
        cls.condition_partner_has_contact_green = cls.env.ref(
            'generic_condition.demo_condition_partner_has_contact_green')
        cls.condition_partner_has_only_contacts = cls.env.ref(
            'generic_condition.demo_condition_partner_has_only_contacts')

    def test_00_defaults(self):
        defaults = self.Condition.default_get(
            self.Condition._fields.keys())

        condition = self.Condition.new(defaults)
        self.assertTrue(condition.enable_caching)
        self.assertTrue(condition.active)
        self.assertEqual(condition.type, 'filter')

    def test_01_defaults_based_on(self):
        defaults = self.Condition.with_context(
            default_based_on='res.partner').default_get(
                self.Condition._fields.keys())

        condition = self.Condition.new(defaults)
        self.assertTrue(condition.enable_caching)
        self.assertTrue(condition.active)
        self.assertEqual(condition.type, 'filter')
        self.assertEqual(condition.model_id.model, 'res.partner')

    def test_02_compute_rel_model_id(self):
        condition = self.condition_partner_has_only_contacts
        self.assertEqual(
            condition.condition_rel_field_id_model_id.model,
            'res.partner')

    @mute_logger('openerp.addons.generic_condition.models.generic_condition')
    def test_05_condtion_eval_error(self):
        with self.assertRaises(ValidationError):
            self.condition_eval_error.check(self.partner_sx_corp)

    def test_10_condition_partner_sx_corp(self):
        condition = self.condition_partner_sx_corp
        self.assertTrue(condition.check(self.partner_sx_corp))
        self.assertFalse(condition.check(self.partner_demo))

    def test_15_condition_partner_not_sx_corp(self):
        condition = self.condition_partner_not_sx_corp
        self.assertFalse(condition.check(self.partner_sx_corp))
        self.assertTrue(condition.check(self.partner_demo))

    def test_20_condition_partner_city_kyiv(self):
        condition = self.condition_partner_city_kyiv
        self.assertTrue(condition.check(self.partner_sx_corp))
        self.assertFalse(condition.check(self.partner_demo))

    def test_25_condition_partner_not_sx_corp_but_kyiv(self):
        condition = self.condition_partner_not_sx_corp_but_kyiv
        self.assertTrue(condition.check(self.partner_z_corp))
        self.assertFalse(condition.check(self.partner_sx_corp))
        self.assertFalse(condition.check(self.partner_demo))

    def test_30_condition_partner_has_contact_green(self):
        condition = self.condition_partner_has_contact_green
        self.assertTrue(condition.check(self.partner_z_corp))
        self.assertFalse(condition.check(self.partner_sx_corp))
        self.assertFalse(condition.check(self.partner_demo))

    def test_35_condition_partner_has_only_contacts(self):
        condition = self.condition_partner_has_only_contacts
        self.assertTrue(condition.check(self.partner_z_corp))
        self.assertFalse(condition.check(self.partner_sx_corp))
        self.assertFalse(condition.check(self.partner_demo))

    def test_40_test_condition_wizard(self):
        Wizard = self.env['generic.condition.test_condition']

        condition = self.condition_partner_has_only_contacts

        wiz = Wizard.create({'condition_id': condition.id})

        wiz.write({'res_id': self.partner_z_corp.id})
        wiz.process()
        self.assertEqual(wiz.result, _('Ok'))

        wiz.write({'res_id': self.partner_sx_corp.id})
        wiz.process()
        self.assertEqual(wiz.result, _('Fail'))

        wiz.write({'res_id': -42})  # ID that are not present in table
        with self.assertRaises(ValidationError):
            wiz.process()
