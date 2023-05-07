import logging
from odoo.tests.common import TransactionCase
_logger = logging.getLogger(__name__)

try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except (ImportError, IOError):  # noqa
    _logger.warning(  # noqa
        "freezegun not installed. Tests will not work!")  # noqa


class TestConditionCheckFind(TransactionCase):
    # Here we have to test Check & find conditions
    # For this case, we will try to find and check calendar meetings related
    # to partner and surveys related to partner.
    # Basic checks are performed to check if there was any meeting with partner
    # during last year (possibly with additional conditions) and to check
    # if we have sent to partner survey (possibly specific one)
    # during last year
    #
    # For these tests we will use two partners:
    # - IT Group (city: Kyiv)
    # - Consulting Group (city: Dnipro)
    # - Development Group (city: Kharkiv) (no predefined meetings)
    # There were two meetings:
    # - with IT Group at 2021-02-03 in Kyiv
    # - with Consulting Group at 2020-09-27 in Lviv
    # There 1 survey:
    # - Feedback Form for IT Group (created 2021-03-13 13:13:13)

    @classmethod
    def setUpClass(cls):
        super(TestConditionCheckFind, cls).setUpClass()

        cls.partner_it_group = cls.env.ref(
            'generic_condition_test.demo_partner_it_group')
        cls.partner_consulting_group = cls.env.ref(
            'generic_condition_test.demo_partner_consulting_group')
        cls.partner_dev_group = cls.env.ref(
            'generic_condition_test.demo_partner_dev_group')

    def test_meeting_with_partner_last_year(self):
        # In this case we test condition with single leaf,
        # that have to be pretty simple
        condition = self.env.ref(
            'generic_condition_test.'
            'test_condition_last_partner_meeting_1_year_ago')
        self.assertTrue(condition.check(self.partner_it_group))
        self.assertTrue(condition.check(self.partner_consulting_group))
        self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        # We can set "If Not Found evaluate to True option on condition,
        # and then checking dev group will evaluate to True,
        # because there are no meetings for dev group
        condition.condition_find_if_not_found = "true"

        self.assertTrue(condition.check(self.partner_it_group))
        self.assertTrue(condition.check(self.partner_consulting_group))
        self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

    def test_meeting_with_partner_last_year__partner_city(self):
        # In this test, we have to test condition with two leaves
        # (same partner, and same city)
        condition = self.env.ref(
            'generic_condition_test.'
            'test_condition_last_partner_meeting_1_year_ago_city')

        self.assertTrue(condition.check(self.partner_it_group))
        self.assertFalse(condition.check(self.partner_consulting_group))
        self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            # Consulting Group had meeting for last year,
            # but it was in different city
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        # We can set "If Not Found evaluate to True option on condition,
        # and then checking dev group will evaluate to True,
        # because there are no meetings for dev group
        condition.condition_find_if_not_found = "true"

        self.assertTrue(condition.check(self.partner_it_group))
        self.assertTrue(condition.check(self.partner_consulting_group))
        self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            # Consulting Group had meeting for last year,
            # but it was in different city
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            # Consulting Group had meeting for last year,
            # but it was in different city
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

    def test_meeting_with_partner_last_year__partner_city_or_lviv(self):
        # In this test, we have to test condition with two leaves
        # (same partner and (same city or location is lviv)
        condition = self.env.ref(
            'generic_condition_test.'
            'test_condition_last_partner_meeting_1_year_ago_city_or_lviv')

        self.assertTrue(condition.check(self.partner_it_group))
        self.assertTrue(condition.check(self.partner_consulting_group))
        self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertFalse(condition.check(self.partner_dev_group))

        # We can set "If Not Found evaluate to True option on condition,
        # and then checking dev group will evaluate to True,
        # because there are no meetings for dev group
        condition.condition_find_if_not_found = "true"

        self.assertTrue(condition.check(self.partner_it_group))
        self.assertTrue(condition.check(self.partner_consulting_group))
        self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-10-02'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertTrue(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

        with freeze_time('2021-08-13'):
            self.assertFalse(condition.check(self.partner_it_group))
            self.assertFalse(condition.check(self.partner_consulting_group))
            self.assertTrue(condition.check(self.partner_dev_group))

    def test_survey_feedback_for_partner_1_year_ago(self):
        # Survey Feedback Form for IT Group (created 2021-03-13 13:13:13)
        condition = self.env.ref(
            'generic_condition_test.'
            'test_condition_crm_partner_survey_sent_year_ago')

        lead_it_group = self.env.ref(
            'generic_condition_test.crm_lead_it_group')
        lead_dev_group = self.env.ref(
            'generic_condition_test.crm_lead_dev_group')

        self.assertTrue(condition.check(lead_it_group))
        self.assertFalse(condition.check(lead_dev_group))

        with freeze_time('2021-08-13'):
            self.assertFalse(condition.check(lead_it_group))
            self.assertFalse(condition.check(lead_dev_group))
