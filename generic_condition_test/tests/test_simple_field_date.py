from odoo.tests.common import SavepointCase


class TestConditionSimpleFieldDate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionSimpleFieldDate, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')
        cls.TestModel = cls.env[cls.test_model.model]

        cls.test_field_date = cls.test_model.field_id.filtered(
            lambda r: r.name == 'date_test')
        cls.test_field_datetime = cls.test_model.field_id.filtered(
            lambda r: r.name == 'datetime_test')

        cls.Condition = cls.env['generic.condition']
        cls.condition_data = {
            "name": 'Simple field condition',
            "model_id": cls.test_model.id,
            "type": 'simple_field',
        }

    def _create_condition(self, data):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_data.copy()
        condition_data.update(data)
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def _check_condition_date(self, val1, val2, operator):
        """ Test date values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_date.id,
            'condition_simple_field_value_date': val2,
            'condition_simple_field_date_operator': operator,
        })
        return condition.check(self._create_record(date_test=val1))

    def _check_condition_datetime(self, val1, val2, operator):
        """ Test datetime values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_datetime.id,
            'condition_simple_field_value_datetime': val2,
            'condition_simple_field_date_operator': operator,
        })
        return condition.check(self._create_record(datetime_test=val1))

    def test_simple_field_date(self):
        self.assertTrue(self._check_condition_date(
            '2022-06-07', '2022-06-07', '='))
        self.assertFalse(self._check_condition_date(
            '2022-06-07', '2022-06-08', '='))

        self.assertFalse(self._check_condition_date(
            '2022-06-07', '2022-06-07', '!='))
        self.assertTrue(self._check_condition_date(
            '2022-06-07', '2022-06-08', '!='))

        self.assertTrue(self._check_condition_date(
            '2022-06-07', False, 'set'))
        self.assertFalse(self._check_condition_date(
            False, False, 'set'))

        self.assertTrue(self._check_condition_date(
            False, False, 'not set'))
        self.assertFalse(self._check_condition_date(
            '2022-06-07', False, 'not set'))

    def test_simple_field_datetime(self):
        self.assertTrue(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-07 16:05:01', '='))
        self.assertFalse(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-08 16:05:01', '='))
        self.assertFalse(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-07 16:05:02', '='))

        self.assertFalse(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-07 16:05:01', '!='))
        self.assertTrue(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-08 16:05:01', '!='))
        self.assertTrue(self._check_condition_datetime(
            '2022-06-07 16:05:01', '2022-06-07 16:05:02', '!='))

        self.assertTrue(self._check_condition_datetime(
            '2022-06-07 16:05:01', False, 'set'))
        self.assertFalse(self._check_condition_datetime(
            False, False, 'set'))

        self.assertTrue(self._check_condition_datetime(
            False, False, 'not set'))
        self.assertFalse(self._check_condition_datetime(
            '2022-06-07 16:05:01', False, 'not set'))
