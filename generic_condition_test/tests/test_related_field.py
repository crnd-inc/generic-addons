from odoo.tests.common import SavepointCase


class TestConditionRelatedField(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestConditionRelatedField, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')
        cls.test_model_relation = cls.env.ref(
            'generic_condition_test.'
            'model_test_generic_condition_test_model_relation')

        cls.TestModel = cls.env[cls.test_model.model]
        cls.TestRelatedModel = cls.env[cls.test_model_relation.model]

        cls.Condition = cls.env['generic.condition']
        cls.condition_data = {
            "name": 'Related field condition',
            "model_id": cls.test_model.id,
            "type": 'related_field',
        }

    def _create_condition(self, field_name, operator, value=False):
        """ Simple helper to create new condition with some predefined values
        """
        field = self.test_model.field_id.filtered(
            lambda r: r.name == field_name)

        condition_data = self.condition_data.copy()
        condition_data.update({
            'condition_related_field_field_id': field.id,
            'condition_related_field_operator': operator,
            'condition_related_field_value_id': value,
        })
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def test_10_related_condition_m2o_set(self):
        condition = self._create_condition('test_m2o', 'set')

        rec = self._create_record(test_m2o=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(test_m2o=self.TestRelatedModel.create({}).id)
        self.assertTrue(condition.check(rec))

    def test_15_related_condition_m2o_not_set(self):
        condition = self._create_condition('test_m2o', 'not set')

        rec = self._create_record(test_m2o=False)
        self.assertTrue(condition.check(rec))
        rec = self._create_record(test_m2o=self.TestRelatedModel.create({}).id)
        self.assertFalse(condition.check(rec))

    def test_20_related_condition_m2o_contains(self):
        related_rec = self.TestRelatedModel.create({})
        related_rec_2 = self.TestRelatedModel.create({})
        condition = self._create_condition(
            'test_m2o', 'contains', related_rec.id)

        rec = self._create_record(test_m2o=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(test_m2o=related_rec.id)
        self.assertTrue(condition.check(rec))
        rec = self._create_record(test_m2o=related_rec_2.id)
        self.assertFalse(condition.check(rec))

    def test_25_related_condition_m2m_set(self):
        condition = self._create_condition('test_m2m', 'set')

        rec = self._create_record(test_m2m=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(
            test_m2m=[(0, 0, {})])
        self.assertTrue(condition.check(rec))

    def test_30_related_condition_m2m_not_set(self):
        condition = self._create_condition('test_m2m', 'not set')

        rec = self._create_record(test_m2m=False)
        self.assertTrue(condition.check(rec))
        rec = self._create_record(
            test_m2m=[(0, 0, {})])
        self.assertFalse(condition.check(rec))

    def test_35_related_condition_m2m_contains(self):
        related_rec = self.TestRelatedModel.create({})
        related_rec_2 = self.TestRelatedModel.create({})
        condition = self._create_condition(
            'test_m2m', 'contains', related_rec.id)

        rec = self._create_record(
            test_m2m=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(
            test_m2m=[(4, related_rec.id)])
        self.assertTrue(condition.check(rec))
        rec = self._create_record(
            test_m2m=[(4, related_rec_2.id)])
        self.assertFalse(condition.check(rec))
        rec = self._create_record(
            test_m2m=[(4, related_rec.id),
                      (4, related_rec_2.id)])
        self.assertTrue(condition.check(rec))
