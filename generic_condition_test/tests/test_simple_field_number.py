from odoo.tests.common import TransactionCase


class TestConditionSimpleFieldNumber(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionSimpleFieldNumber, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')
        cls.TestModel = cls.env[cls.test_model.model]

        cls.test_field_int = cls.test_model.field_id.filtered(
            lambda r: r.name == 'test_int')
        cls.test_field_float = cls.test_model.field_id.filtered(
            lambda r: r.name == 'test_float')

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

    def _check_integer_condition(self, val1, val2, operator):
        """ Test integer values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_int.id,
            'condition_simple_field_value_integer': val2,
            'condition_simple_field_number_operator': operator,
        })
        return condition.check(self._create_record(test_int=val1))

    def _check_float_condition(self, val1, val2, operator):
        """ Test float values
        """
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_float.id,
            'condition_simple_field_value_float': val2,
            'condition_simple_field_number_operator': operator,
        })
        return condition.check(self._create_record(test_float=val1))

    def test_10_simple_field_integer(self):
        self.assertTrue(self._check_integer_condition(42, 42, '='))
        self.assertFalse(self._check_integer_condition(42, 30, '='))

        self.assertTrue(self._check_integer_condition(42, 30, '!='))
        self.assertFalse(self._check_integer_condition(42, 42, '!='))

        self.assertTrue(self._check_integer_condition(42, 30, '>'))
        self.assertFalse(self._check_integer_condition(42, 42, '>'))
        self.assertFalse(self._check_integer_condition(42, 45, '>'))

        self.assertTrue(self._check_integer_condition(30, 42, '<'))
        self.assertFalse(self._check_integer_condition(42, 42, '<'))
        self.assertFalse(self._check_integer_condition(45, 42, '<'))

        self.assertTrue(self._check_integer_condition(42, 30, '>='))
        self.assertTrue(self._check_integer_condition(42, 42, '>='))
        self.assertFalse(self._check_integer_condition(42, 45, '>='))

        self.assertTrue(self._check_integer_condition(30, 42, '<='))
        self.assertTrue(self._check_integer_condition(42, 42, '<='))
        self.assertFalse(self._check_integer_condition(45, 42, '<='))

    def test_10_simple_field_float(self):
        self.assertTrue(self._check_float_condition(42.7, 42.7, '='))
        self.assertFalse(self._check_float_condition(42.2, 42.3, '='))
        self.assertFalse(self._check_float_condition(42, 30, '='))

        self.assertTrue(self._check_float_condition(42, 30, '!='))
        self.assertFalse(self._check_float_condition(42, 42, '!='))

        self.assertTrue(self._check_float_condition(42, 30, '>'))
        self.assertFalse(self._check_float_condition(42, 42, '>'))
        self.assertFalse(self._check_float_condition(42, 45, '>'))

        self.assertTrue(self._check_float_condition(30, 42, '<'))
        self.assertFalse(self._check_float_condition(42, 42, '<'))
        self.assertFalse(self._check_float_condition(45, 42, '<'))

        self.assertTrue(self._check_float_condition(42, 30, '>='))
        self.assertTrue(self._check_float_condition(42, 42, '>='))
        self.assertFalse(self._check_float_condition(42, 45, '>='))

        self.assertTrue(self._check_float_condition(30, 42, '<='))
        self.assertTrue(self._check_float_condition(42, 42, '<='))
        self.assertFalse(self._check_float_condition(45, 42, '<='))
