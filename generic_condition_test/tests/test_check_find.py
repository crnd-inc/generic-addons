import datetime
import logging
from odoo.tests.common import SavepointCase
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

try:
    # pylint: disable=unused-import
    from freezegun import freeze_time  # noqa
except (ImportError, IOError):  # noqa
    _logger.warning(  # noqa
        "freezegun not installed. Tests will not work!")  # noqa


class TestConditionCheckFind(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionCheckFind, cls).setUpClass()

        # m2m_m2o leaf tests
        cls.test_partner1 = cls.env.ref(
            'generic_condition_test.demo_partner_it_group')
        cls.test_partner2 = cls.env.ref(
            'generic_condition_test.demo_partner_consulting_group')
        cls.event = cls.env.ref(
            'generic_condition_test.calendar_event_test'
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

        # m2o_m2o leaf tests
        cls.condition_m2o = cls.env.ref(
            'generic_condition_test'
            '.test_condition_partners_survey_sent_year_ago'
        )
        cls.survey = cls.env.ref(
            'survey.feedback_form'
        )

    def test_m2m_m2o_condition_type_find_check(self):
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

    def test_m2o_m2o_condition_type_find_check(self):

        # Create and send survey message to partner
        survey_mail_message = self.env['survey.mail.compose.message'].create({
            'survey_id': self.survey.id, 'public': 'email_private',
            'body': '__URL__', 'partner_ids': [(4, self.test_partner1.id)]})
        survey_mail_message.send_mail()

        # Check that survey sent to partner less than year ago
        self.assertFalse(self.condition_m2o.check(self.test_partner1))

        # Check that message was sent to partner year ago
        date_over_year = datetime.date.today() + relativedelta(days=368)
        with freeze_time(date_over_year.strftime('%Y-%m-%d')):
            self.assertTrue(self.condition_m2o.check(self.test_partner1))
