from odoo.tests.common import SavepointCase


class TestConditionSimpleFieldBoolean(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionSimpleFieldBoolean, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')

        cls.TestModel = cls.env[cls.test_model.model]

        cls.test_field_bool = cls.test_model.field_id.filtered(
            lambda r: r.name == 'test_bool')

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

    def test_10_simple_field_boolean__true__True(self):
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_bool.id,
            'condition_simple_field_value_boolean': 'true',
        })
        rec = self.TestModel.create({'test_bool': True})
        self.assertTrue(condition.check(rec))

    def test_11_simple_field_boolean__true__False(self):
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_bool.id,
            'condition_simple_field_value_boolean': 'true',
        })
        rec = self.TestModel.create({'test_bool': False})
        self.assertFalse(condition.check(rec))

    def test_12_simple_field_boolean__false__False(self):
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_bool.id,
            'condition_simple_field_value_boolean': 'false',
        })
        rec = self.TestModel.create({'test_bool': False})
        self.assertTrue(condition.check(rec))

    def test_13_simple_field_boolean__false__True(self):
        condition = self._create_condition({
            'condition_simple_field_field_id': self.test_field_bool.id,
            'condition_simple_field_value_boolean': 'false',
        })
        rec = self.TestModel.create({'test_bool': True})
        self.assertFalse(condition.check(rec))
