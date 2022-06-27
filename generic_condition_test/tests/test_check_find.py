from odoo.tests.common import SavepointCase


class TestConditionCheckFind(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionCheckFind, cls).setUpClass()
        cls.test_partner1 = cls.env.ref(
            'generic_condition_test.demo_partner_it_group')
        cls.test_partner2 = cls.env.ref(
            'generic_condition_test.demo_partner_consulting_group'
        )
        cls.condition = cls.env.ref(
            "generic_condition_test"
            ".test_condition_event_year_ago_on_partner_area"
        )
        cls.condition_location_leaf = cls.env.ref(
            "generic_condition_test"
            ".test_condition_leaf_event_location_equals_partner_location"
        )
        cls.condition_logic_operator_leaf = cls.env.ref(
            "generic_condition_test.test_condition_logic_operator"
        )

    def test_condition_type_find_check(self):
        # Check following conditions:
        # - partner city same as event location AND
        # - partner in Attendees;
        # - event created more than year ago
        self.assertTrue(self.condition.check(self.test_partner1))
        self.assertFalse(self.condition.check(self.test_partner2))

        # Change logical operator to 'OR'
        self.condition_logic_operator_leaf.write({
            'type': 'operator-or',
        })
        # Check following conditions:
        # - partner city same as event location OR
        # - partner in Attendees;
        # - event created more than year ago
        self.assertTrue(self.condition.check(self.test_partner1))
        self.assertTrue(self.condition.check(self.test_partner2))
