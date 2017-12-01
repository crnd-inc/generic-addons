# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp import fields


class TestConditionMonetaryField(TransactionCase):
    def setUp(self):
        super(TestConditionMonetaryField, self).setUp()
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])
        self.TestModel = self.env[self.test_model.model]
        self.usd = self.env.ref('base.USD')
        self.uah = self.env.ref('base.UAH')
        self.vals = {
            'test_1_monetary': 150,
            'test_1_monetary_currency': self.usd.id,
            'date_test': '2012-05-03'
        }
        self.test_monetary = self.TestModel.create(self.vals)

        self.Condition = self.env['generic.condition']
        self.condition_data = {
            "name": 'Monetary field condition',
            "model_id": self.test_model.id,
            "type": 'monetary_field',
        }
        self.test_1_monetary = self.test_model.field_id.filtered(
            lambda r: r.name == 'test_1_monetary')
        self.test_1_monetary_currency = self.test_model.field_id.filtered(
            lambda r: r.name == 'test_1_monetary_currency')
        self.condition_currency_date_field = self.test_model.field_id.filtered(
            lambda r: r.name == 'date_test')
        self.date_field_map = {
            'now': fields.Datetime.now(),
            'field': 'condition_currency_date_field',
            'date': 'condition_currency_date_date',
            'datetime': 'condition_currency_date_datetime'
        }

    def _create_condition(self, data):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_data.copy()
        condition_data.update(data)
        return self.Condition.create(condition_data)

    def _check_monetary_condition(self, val, operator, val_currency,
                                  date_type, currency_date):
        """ Test integer values
        """
        vals = {
            'condition_monetary_field': self.test_1_monetary.id,
            'condition_monetary_currency_field':
                self.test_1_monetary_currency.id,
            'condition_monetary_operator': operator,
            'condition_monetary_value': val,
            'condition_monetary_currency_value': val_currency.id,
            'condition_currency_date_type': date_type
        }
        if date_type != 'now':
            vals.update({self.date_field_map[date_type]: currency_date})
        condition = self._create_condition(vals)
        return condition.check(self.test_monetary)

    def _currency_exchange(self, ctx_date, val_currency):
        return (
            self.test_monetary[self.test_1_monetary_currency.name].
            with_context(date=ctx_date).
            compute(self.test_monetary[self.test_1_monetary.name],
                    val_currency))

    def test_monetary_field_with_date_type_field(self):
        # tests with date_type field
        date = self.condition_currency_date_field
        ctx_date = self.test_monetary[self.condition_currency_date_field.name]
        val_currency = self.uah
        val = self._currency_exchange(ctx_date, val_currency)

        self.assertTrue(self._check_monetary_condition(
            val, '=', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val, '!=', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val, '>', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val, '<', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val, '>=', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val, '<=', val_currency, 'field', date.id))

        val1 = val + 10

        self.assertFalse(self._check_monetary_condition(
            val1, '=', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val1, '!=', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val1, '>', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val1, '<', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val1, '>=', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val1, '<=', val_currency, 'field', date.id))

        val2 = val - 10

        self.assertFalse(self._check_monetary_condition(
            val2, '=', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val2, '!=', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val2, '<', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val2, '>', val_currency, 'field', date.id))
        self.assertTrue(self._check_monetary_condition(
            val2, '<=', val_currency, 'field', date.id))
        self.assertFalse(self._check_monetary_condition(
            val2, '>=', val_currency, 'field', date.id))

    def test_monetary_field_with_date_type_date(self):
        # tests with date_type date
        date = '2012-05-03'
        val_currency = self.uah
        val = self._currency_exchange(date, val_currency)

        self.assertTrue(self._check_monetary_condition(
            val, '=', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val, '!=', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val, '>', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val, '<', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val, '>=', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val, '<=', val_currency, 'date', date))

        val1 = val + 10

        self.assertFalse(self._check_monetary_condition(
            val1, '=', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '!=', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>=', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<=', val_currency, 'date', date))

        val2 = val - 10

        self.assertFalse(self._check_monetary_condition(
            val2, '=', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '!=', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>', val_currency, 'date', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<=', val_currency, 'date', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>=', val_currency, 'date', date))

    def test_monetary_field_with_date_type_datetime(self):
        # tests with date_type datetime
        date = '2017-05-01 13:31:14'
        val_currency = self.uah
        val = self._currency_exchange(date, val_currency)

        self.assertTrue(self._check_monetary_condition(
            val, '=', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val, '!=', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val, '>', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val, '<', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val, '>=', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val, '<=', val_currency, 'datetime', date))

        val1 = val + 10

        self.assertFalse(self._check_monetary_condition(
            val1, '=', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '!=', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>=', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<=', val_currency, 'datetime', date))

        val2 = val - 10

        self.assertFalse(self._check_monetary_condition(
            val2, '=', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '!=', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>', val_currency, 'datetime', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<=', val_currency, 'datetime', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>=', val_currency, 'datetime', date))

    def test_monetary_field_with_date_type_now(self):
        # tests with date_type now
        date = self.date_field_map['now']
        val_currency = self.uah
        val = self._currency_exchange(date, val_currency)

        self.assertTrue(self._check_monetary_condition(
            val, '=', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val, '!=', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val, '>', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val, '<', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val, '>=', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val, '<=', val_currency, 'now', date))

        val1 = val + 10

        self.assertFalse(self._check_monetary_condition(
            val1, '=', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '!=', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val1, '>=', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val1, '<=', val_currency, 'now', date))

        val2 = val - 10

        self.assertFalse(self._check_monetary_condition(
            val2, '=', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '!=', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>', val_currency, 'now', date))
        self.assertTrue(self._check_monetary_condition(
            val2, '<=', val_currency, 'now', date))
        self.assertFalse(self._check_monetary_condition(
            val2, '>=', val_currency, 'now', date))
