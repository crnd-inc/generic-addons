from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestCondition(TransactionCase):
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

    def test_05_condition_filter(self):
        with self.assertRaises(ValidationError):
            self.env['generic.condition'].create({
                'name': 'test',
                'model_id': self.ref('base.model_res_country'),
                'type': 'filter',
                'condition_filter_id': self.ref(
                    'generic_condition.demo_filter_partner_city_kyiv'),
            })

    def test_10_condition_condition(self):
        with self.assertRaises(ValidationError):
            self.env['generic.condition'].create({
                'name': 'test',
                'model_id': self.ref('base.model_res_country'),
                'type': 'condition',
                'condition_condition_id': self.condition_partner_sx_corp.id,
            })

    def test_15_condition_group(self):
        c_condition = self.env['generic.condition'].create({
            'name': 'test country',
            'model_id': self.ref('base.model_res_country'),
            'type': 'eval',
            'condition_eval': 'record.name == "United States"',
        })

        # no error if right condition
        self.env['generic.condition'].create({
            'name': 'test',
            'model_id': self.ref('base.model_res_country'),
            'type': 'condition_group',
            'condition_condition_ids': [
                (6, 0, [c_condition.id])],
        })

        # error if there are conditions for wrong model
        with self.assertRaises(ValidationError):
            self.env['generic.condition'].create({
                'name': 'test',
                'model_id': self.ref('base.model_res_country'),
                'type': 'condition_group',
                'condition_condition_ids': [
                    (6, 0, [
                        c_condition.id,
                        self.ref(
                            'generic_condition.'
                            'demo_condition_partner_not_sx_corp'),
                        self.ref(
                            'generic_condition.'
                            'demo_condition_partner_city_kyiv')])],
            })
