from odoo.tests.common import SavepointCase


class TestConditionCheckFind(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionCheckFind, cls).setUpClass()
        cls.test_partner = cls.env.ref(
            'generic_condition_test.demo_partner_it_group')
        cls.condition = cls.env.ref(
            "generic_condition_test"
            ".test_condition_event_year_ago_on_partner_area"
        )
        cls.condition_leaf = cls.env.ref(
            "generic_condition_test"
            ".test_condition_leaf_event_location_equals_partner_location"
        )

    def test_condition_type_find_check(self):
        self.assertTrue(self.condition.check(self.test_partner))
        self.condition_leaf.write({
            'value_field_operator': '!=',
        })
        self.assertFalse(self.condition.check(self.test_partner))
