from openerp.tests.common import SavepointCase
import datetime


class TestConditionMonetaryField(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionMonetaryField, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')

        # Models
        cls.TestModel = cls.env[cls.test_model.model]
        cls.Condition = cls.env['generic.condition']

        # Currencies
        cls.usd = cls.env.ref('base.USD')
        cls.eur = cls.env.ref('base.EUR')

        # Test record
        # 150 USD on 2012-05-03
        cls.test_monetary = cls.env.ref(
            'generic_condition_test.test_generic_condition_model_rec_monetary')

        # Test condition
        # Checks if test record's test_monetary field is equal to $150
        cls.test_condition = cls.env.ref(
            'generic_condition_test.test_condition_monetary_equal_150_usd')

    def _check_monetary_condition(self, operator, val, val_currency,
                                  date_type='now', currency_date=None):
        vals = {
            'condition_monetary_operator': operator,
            'condition_monetary_value': val,
            'condition_monetary_value_currency_id': val_currency.id,
            'condition_monetary_curency_date_type': date_type
        }
        if date_type == 'date':
            self.assertIsNotNone(currency_date)
            vals.update({
                'condition_monetary_curency_date_date': currency_date,
            })

        self.test_condition.write(vals)
        return self.test_condition.check(self.test_monetary)

    def test_monetary_field_same_currency_no_rate(self):
        # Ensure same currency
        self.assertEqual(self.test_monetary.test_monetary_currency, self.usd)
        self.assertEqual(
            self.test_condition.condition_monetary_value_currency_id, self.usd)

        # Test record (150 usd) against 150 usd
        self.assertTrue(self._check_monetary_condition(
            '=', 150.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '!=', 150.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '>', 150.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '<', 150.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '>=', 150.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '<=', 150.0, self.usd, date_type='now'))

        # Test record (150 usd) against 140 usd
        self.assertFalse(self._check_monetary_condition(
            '=', 140.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '!=', 140.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '>', 140.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '<', 140.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '>=', 140.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '<=', 140.0, self.usd, date_type='now'))

        # Test record(150 usd)  against 160 usd
        self.assertFalse(self._check_monetary_condition(
            '=', 160.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '!=', 160.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '>', 160.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '<', 160.0, self.usd, date_type='now'))
        self.assertFalse(self._check_monetary_condition(
            '>=', 160.0, self.usd, date_type='now'))
        self.assertTrue(self._check_monetary_condition(
            '<=', 160.0, self.usd, date_type='now'))

    def test_monetary_field_different_currencies_fixed_date(self):
        # This test is based on currency rate's demo data
        # It includes following
        #   - company currency is EUR
        #   - USD to EUR
        #     - 2010-01-01: 1.2834
        #     - %Y-06-06: 1.5289
        #
        # We define two dates that should be used as accounting date:
        #   - date_1 = '2010-01-05'
        #   - date_2 = '%Y-07-03'
        #
        # These dates should use following rates:
        #   - date_1 - 1.2834
        #   - date_2 - 1.5289
        #
        # In this test we change currency of record to euro
        # thus record's 'test_monetary' field is 150 EUR
        # which is:
        #   - on 2010-01-01+: 150 * 1.2834 = 192.51 USD
        #   - on %Y-06-06+:   150 * 1.5289 = 229.34 USD
        #
        date_1 = '2010-01-05'  # rate 1.2834 should be used
        date_2 = datetime.date.today().strftime('%Y-07-03')
        self.test_monetary.test_monetary_currency = self.eur

        # Ensure currencies ok
        self.assertEqual(
            self.test_monetary.test_monetary_currency, self.eur)
        self.assertEqual(
            self.test_condition.condition_monetary_value_currency_id, self.usd)

        # Test record (150 eur) against 192.51 usd on date_1 (2010-01-05)
        # Expected rate 1.2834
        # Expected record val and condition val are equal
        self.assertTrue(self._check_monetary_condition(
            '=', 192.51, self.usd, date_type='date', currency_date=date_1))
        self.assertFalse(self._check_monetary_condition(
            '!=', 192.51, self.usd, date_type='date', currency_date=date_1))
        self.assertFalse(self._check_monetary_condition(
            '>', 192.51, self.usd, date_type='date', currency_date=date_1))
        self.assertFalse(self._check_monetary_condition(
            '<', 192.51, self.usd, date_type='date', currency_date=date_1))
        self.assertTrue(self._check_monetary_condition(
            '>=', 192.51, self.usd, date_type='date', currency_date=date_1))
        self.assertTrue(self._check_monetary_condition(
            '<=', 192.51, self.usd, date_type='date', currency_date=date_1))

        # Test record (150 eur) against 192.51 usd on date_2 (%Y-07-03)
        # Expected rate 1.5289
        # Expected record val is greater then condition val
        self.assertFalse(self._check_monetary_condition(
            '=', 192.51, self.usd, date_type='date', currency_date=date_2))
        self.assertTrue(self._check_monetary_condition(
            '!=', 192.51, self.usd, date_type='date', currency_date=date_2))
        self.assertTrue(self._check_monetary_condition(
            '>', 192.51, self.usd, date_type='date', currency_date=date_2))
        self.assertFalse(self._check_monetary_condition(
            '<', 192.51, self.usd, date_type='date', currency_date=date_2))
        self.assertTrue(self._check_monetary_condition(
            '>=', 192.51, self.usd, date_type='date', currency_date=date_2))
        self.assertFalse(self._check_monetary_condition(
            '<=', 192.51, self.usd, date_type='date', currency_date=date_2))

        # Test record (150 eur) against 229.34 usd on date_2 (%Y-07-03)
        # Expected rate 1.5289
        # Expected record val and condition val are equal
        self.assertTrue(self._check_monetary_condition(
            '=', 229.34, self.usd, date_type='date', currency_date=date_2))
        self.assertFalse(self._check_monetary_condition(
            '!=', 229.34, self.usd, date_type='date', currency_date=date_2))
        self.assertFalse(self._check_monetary_condition(
            '>', 229.34, self.usd, date_type='date', currency_date=date_2))
        self.assertFalse(self._check_monetary_condition(
            '<', 229.34, self.usd, date_type='date', currency_date=date_2))
        self.assertTrue(self._check_monetary_condition(
            '>=', 229.34, self.usd, date_type='date', currency_date=date_2))
        self.assertTrue(self._check_monetary_condition(
            '<=', 229.34, self.usd, date_type='date', currency_date=date_2))

    def test_monetary_field_different_currencies_date_in_date_field(self):
        # This test is based on currency rate's demo data
        # It includes following
        #   - company currency is EUR
        #   - USD to EUR
        #     - 2010-01-01: 1.2834
        #     - %Y-06-06: 1.5289
        #
        # We define two dates that should be used as accounting date:
        #   - date_1 = '2010-01-05'
        #   - date_2 = '%Y-07-03'
        #
        # These dates should use following rates:
        #   - date_1 - 1.2834
        #   - date_2 - 1.5289
        #
        # In this test we change currency of record to euro
        # thus record's 'test_monetary' field is 150 EUR
        # which is:
        #   - on 2010-01-01+: 150 * 1.2834 = 192.51 USD
        #   - on %Y-06-06+:   150 * 1.5289 = 229.34 USD
        #
        # Accounting date now is stored in checked record in 'date_test' field
        date_1 = '2010-01-05'  # rate 1.2834 should be used
        date_2 = datetime.date.today().strftime('%Y-07-03')
        self.test_monetary.test_monetary_currency = self.eur

        # Ensure currencies ok
        self.assertEqual(
            self.test_monetary.test_monetary_currency, self.eur)
        self.assertEqual(
            self.test_condition.condition_monetary_value_currency_id, self.usd)

        # Set date to date_1 (2010-01-05)
        self.test_monetary.date_test = date_1

        # Test record (150 eur) against 192.51 usd on date_1 (2010-01-05)
        # Expected rate 1.2834
        # Expected record val and condition val are equal
        self.assertTrue(self._check_monetary_condition(
            '=', 192.51, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '!=', 192.51, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '>', 192.51, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '<', 192.51, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '>=', 192.51, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '<=', 192.51, self.usd, date_type='field'))

        # Set date to date_2 (%Y-07-03)
        self.test_monetary.date_test = date_2

        # Test record (150 eur) against 192.51 usd on date_2 (%Y-07-03)
        # Expected rate 1.5289
        # Expected record val is greater then condition val
        self.assertFalse(self._check_monetary_condition(
            '=', 192.51, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '!=', 192.51, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '>', 192.51, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '<', 192.51, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '>=', 192.51, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '<=', 192.51, self.usd, date_type='field'))

        # Test record (150 eur) against 229.34 usd on date_2 (%Y-07-03)
        # Expected rate 1.5289
        # Expected record val and condition val are equal
        self.assertTrue(self._check_monetary_condition(
            '=', 229.34, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '!=', 229.34, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '>', 229.34, self.usd, date_type='field'))
        self.assertFalse(self._check_monetary_condition(
            '<', 229.34, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '>=', 229.34, self.usd, date_type='field'))
        self.assertTrue(self._check_monetary_condition(
            '<=', 229.34, self.usd, date_type='field'))
