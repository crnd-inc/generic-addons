from datetime import datetime

from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tools.jinja import (
    render_jinja_string, prepare_jinja_template_env)


class TestJinjaTimezone(TransactionCase):
    """ Test case for jinja timezone conversion functionality """

    def test_as_timezone_function(self):
        """ Test that as_timezone function correctly converts datetime objects
            to different timezones
        """
        # Create a jinja environment
        env = prepare_jinja_template_env()

        # Verify that as_timezone function is available in the env
        self.assertIn('as_timezone', env.globals)
        self.assertIn('pytz', env.globals)

        # Test as_timezone function directly
        as_timezone = env.globals['as_timezone']
        test_date = datetime(2025, 6, 22, 19, 33, 27)

        # Test with default timezone (UTC)
        utc_result = as_timezone(test_date)
        self.assertIsInstance(utc_result, str)
        self.assertEqual(utc_result, '2025-06-22 19:33:27')

        # Test with specific timezone (Kiev/Kyiv)
        kiev_result = as_timezone(test_date, 'Europe/Kiev')
        self.assertIsInstance(kiev_result, str)
        # Kiev is UTC+3, so 19:00 UTC becomes 22:00 Kiev
        self.assertEqual(kiev_result, '2025-06-22 22:33:27')

        # Test with string date
        str_date = "2025-06-22T19:33:27"
        str_result = as_timezone(str_date, 'Europe/Kiev')
        self.assertIsInstance(str_result, str)
        self.assertEqual(str_result, '2025-06-22 22:33:27')

        # Test with None
        none_result = as_timezone(None)
        self.assertIsNone(none_result)

    def test_jinja_template_rendering_with_timezone(self):
        """ Test rendering a jinja template with timezone conversion """
        # Test date
        test_date = datetime(2025, 6, 22, 19, 33, 27)

        template = """
        UTC time: {{ test_date }}
        Kiev time: {{ as_timezone(test_date, 'Europe/Kiev') }}
        New York time: {{ as_timezone(test_date, 'America/New_York') }}
        """

        context = {
            'test_date': test_date,
        }

        result = render_jinja_string(template, context)

        # Check that the rendered result contains
        # the expected timezone conversions
        self.assertIn('UTC time: 2025-06-22 19:33:27', result)
        self.assertIn('Kiev time: 2025-06-22 22:33:27', result)  # UTC+3
        self.assertIn('New York time: 2025-06-22 15:33:27', result)  # UTC-4
