from odoo.tools.misc import mute_logger
import logging
from odoo.tests.common import SavepointCase
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except ImportError:  # pragma: no cover
    logging.getLogger(__name__).warning(
        "freezegun not installed. Tests will not work!")


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
        cls.condition_company_partner_created_year_ago = cls.env.ref(
            'generic_condition.demo_condition_company_partner_created_year_ago'
        )

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

    @mute_logger('odoo.addons.generic_condition.models.generic_condition')
    def test_05_condtion_eval_error(self):
        with self.assertRaises(ValidationError):
            self.condition_eval_error.check(self.partner_sx_corp)

    def test_08_condition_partner_sx_corp_wrong_model(self):
        condition = self.condition_partner_sx_corp
        wrong_obj = self.env['res.country'].search([], limit=1)
        with self.assertRaises(UserError):
            condition.check(wrong_obj)

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

    def test_36_condition_partner_has_only_contacts__access_portal_user(self):
        user = self.env.ref('base.demo_user0')

        self.env['ir.rule'].search(
            [('model_id.model', '=', 'res.partner')],
        ).unlink()

        condition = self.condition_partner_has_only_contacts.sudo(user)
        self.assertTrue(condition.check(self.partner_z_corp.sudo(user)))
        self.assertFalse(condition.check(self.partner_sx_corp.sudo(user)))
        self.assertFalse(condition.check(self.partner_demo.sudo(user)))

    def test_40_test_condition_wizard(self):
        condition = self.condition_partner_has_only_contacts

        wiz_act = condition.action_show_test_wizard()
        wiz = self.env[wiz_act['res_model']].with_context(
            **wiz_act['context']
        ).create({
            'res_id': self.partner_z_corp.id,
        })

        wiz.process()
        self.assertEqual(wiz.result, _('Ok'))

        wiz.write({'res_id': self.partner_sx_corp.id})
        wiz.process()
        self.assertEqual(wiz.result, _('Fail'))

        wiz.write({'res_id': -42})  # ID that are not present in table
        with self.assertRaises(ValidationError):
            wiz.process()

    def test_condition_type_find_check(self):
        date_above_year = datetime.now() + relativedelta(years=1, days=1)
        condition = self.condition_company_partner_created_year_ago
        self.env['res.partner'].create({
            'name': 'Old partner',
            'parent_id': self.env.user.company_id.id,
        })
        self.assertFalse(condition.check(self.env.user.company_id))

        with freeze_time(date_above_year.strftime('%Y-%m-%d')):
            self.assertTrue(condition.check(self.env.user.company_id))
