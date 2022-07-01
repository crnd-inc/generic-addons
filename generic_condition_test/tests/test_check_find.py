import datetime
import logging
from odoo.tests.common import Form, SavepointCase
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

        # m2o_o2m leaf tests
        cls.condition_o2m_o2m = cls.env.ref(
            'generic_condition_test.test_condition_contact_has_lead_partner')

        # m2m_o2m leaf tests
        cls.condition_m2m_o2m = cls.env.ref(
            'generic_condition_test'
            '.test_condition_contact_has_partners_active_calendar_events')

    def test_m2m_m2o_condition_type_find_check(self):
        # Create condition leaf for existing condition
        # Use Form class to trigger onchange
        with Form(self.condition) as condition:
            with condition.condition_find_search_domain_ids.new() as leaf:
                leaf.type = 'search-condition'
                leaf.check_field_id = self.env.ref(
                    'calendar.field_calendar_event__location')
                leaf.value_field_operator = '='
                leaf.value_field_id = self.env.ref(
                    'base.field_res_partner__city')

        # Check following conditions:
        # - partner city same as event location AND
        # - partner in Attendees;
        # - event created more than year ago
        self.assertTrue(self.condition.check(self.test_partner1))
        self.assertFalse(self.condition.check(self.test_partner2))

        # Change logical operator to 'OR' (use Form class to trigger onchange)
        condition_form = Form(self.condition_logic_operator_leaf)
        condition_form.type = 'operator-or'
        condition_form.save()

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

        # Check that survey was sent to partner less than year ago
        self.assertFalse(self.condition_m2o.check(self.test_partner1))

        # Check that message was sent to partner year ago
        date_over_year = datetime.date.today() + relativedelta(days=368)
        with freeze_time(date_over_year.strftime('%Y-%m-%d')):
            self.assertTrue(self.condition_m2o.check(self.test_partner1))

    def test_m2o_o2m_condition_type_find_check(self):
        # Create condition leaf for existing condition
        # Use Form class to trigger onchange
        with Form(self.condition_o2m_o2m) as condition:
            with condition.condition_find_search_domain_ids.new() as leaf:
                leaf.type = 'search-condition'
                leaf.check_field_id = self.env.ref(
                    'crm.field_crm_lead__partner_id')
                leaf.value_field_operator = '='
                leaf.value_field_id = self.env.ref(
                    'base.field_res_partner__child_ids')

        # Create partner, child partner
        parent_partner = self.env['res.partner'].create({
            'name': 'Grand partner',
        })
        child_partner = self.env['res.partner'].create({
            'name': 'Child partner',
            'parent_id': parent_partner.id,
        })

        # Check that child partner doesn't have lead
        self.assertFalse(self.condition_o2m_o2m.check(parent_partner))

        # Create opportunity for child partner
        self.env['crm.lead'].create({
            'type': "opportunity",
            'name': "Test lead child partner",
            'partner_id': child_partner.id,
            'description': "Opportunity for child partner",
        })

        # Check that child partner has lead
        self.assertTrue(self.condition_o2m_o2m.check(parent_partner))

    def test_m2m_o2m_condition_type_find_check(self):
        # Contacts has no child
        self.assertFalse(self.condition_m2m_o2m.check(self.test_partner1))
        self.assertFalse(self.condition_m2m_o2m.check(self.test_partner2))

        # Make child partner
        self.test_partner2.write({
            'parent_id': self.test_partner1.id
        })

        # Check that contact has child with active calendar event
        self.assertFalse(self.condition_m2m_o2m.check(self.test_partner2))
        self.assertTrue(self.condition_m2m_o2m.check(self.test_partner1))
