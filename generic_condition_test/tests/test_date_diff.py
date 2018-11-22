from odoo.tests.common import SavepointCase

try:
    from freezegun import freeze_time
except ImportError:  # pragma: no cover
    import logging
    logging.getLogger(__name__).warn(
        "freezegun not installed. Tests will not work!")


class TestConditionDateDiff(SavepointCase):
    """ This test case requires creation of separate model with at least
        two date / datetime fields, so it is implemented as separate test case
        in separate addon.
    """

    @classmethod
    def setUpClass(cls):
        super(TestConditionDateDiff, cls).setUpClass()
        cls.test_model = cls.env.ref(
            'generic_condition_test.model_test_generic_condition_test_model')

        cls.TestModel = cls.env[cls.test_model.model]
        cls.test_field_start_date = cls.test_model.field_id.filtered(
            lambda r: r.name == 'date_start')
        cls.test_field_end_date = cls.test_model.field_id.filtered(
            lambda r: r.name == 'date_end')
        cls.test_field_test_date = cls.test_model.field_id.filtered(
            lambda r: r.name == 'date_test')

        cls.Condition = cls.env['generic.condition']
        cls.condition_date_diff_data = {
            "name": 'Date diff fields diff',
            "model_id": cls.test_model.id,
            "type": 'date_diff',
        }

    def _create_condition(self, data):
        """ Simple helper to create new condition with some predefined values
        """
        condition_data = self.condition_date_diff_data.copy()
        condition_data.update(data)
        return self.Condition.create(condition_data)

    def test_10_condition_date_diff(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'field',
            "condition_date_diff_date_end_field": self.test_field_end_date.id,
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })
        self.assertFalse(condition.check(rec))

        condition.condition_date_diff_operator = '!='
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '='
        rec.date_end = '2017-05-03'
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '>'
        self.assertFalse(condition.check(rec))

        condition.condition_date_diff_operator = '<'
        self.assertFalse(condition.check(rec))

        condition.condition_date_diff_operator = '<='
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '>='
        self.assertTrue(condition.check(rec))

        # test date-diff with different field types (datetime and date)
        rec.date_test = '2017-05-04'
        rec.date_start = '2017-05-02'
        condition.write({
            'condition_date_diff_operator': '=',
            'condition_date_diff_date_end_field': self.test_field_test_date.id,
        })
        self.assertTrue(condition.check(rec))

    def test_15_condition_date_diff_similar_dates_hours(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'field',
            "condition_date_diff_date_end_field": self.test_field_end_date.id,
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'hours',
            "condition_date_diff_value": 2,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01 13:31:14',
            'date_end': '2017-05-01 15:31:45',
        })
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '!='
        self.assertFalse(condition.check(rec))

        rec.date_end = '2017-05-01 14:31:45'
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '='
        rec.write({
            'date_start': '2017-05-01 13:31:14',
            'date_end': '2017-05-01 15:34:45',
        })
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '!='
        self.assertFalse(condition.check(rec))

        rec.date_end = '2017-05-01 14:31:45'
        self.assertTrue(condition.check(rec))

    def test_15_condition_date_diff_similar_dates_days(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'field',
            "condition_date_diff_date_end_field": self.test_field_end_date.id,
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01 13:31:14',
            'date_end': '2017-05-03 13:31:45',
        })
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '!='
        self.assertFalse(condition.check(rec))

        rec.date_end = '2017-05-02 13:31:45'
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '='
        rec.write({
            'date_start': '2017-05-01 13:31:14',
            'date_end': '2017-05-03 13:34:45',
        })
        self.assertTrue(condition.check(rec))

        condition.condition_date_diff_operator = '!='
        self.assertFalse(condition.check(rec))

        rec.date_end = '2017-05-10 14:31:45'
        self.assertTrue(condition.check(rec))

    def test_20_condition_date_diff_fixed_date(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'date',
            "condition_date_diff_date_end_date": '2017-05-03',
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })

        self.assertTrue(condition.check(rec))

        rec.date_start = '2017-05-13'

        self.assertFalse(condition.check(rec))

    def test_30_condition_date_diff_fixed_datetime(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'datetime',
            "condition_date_diff_date_end_datetime": '2017-05-03 18:31:41',
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })

        self.assertTrue(condition.check(rec))

        rec.date_start = '2017-05-13 19:13:43'

        self.assertFalse(condition.check(rec))

    def test_40_condition_date_diff_fixed_date_absolute(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'date',
            "condition_date_diff_date_end_date": '2017-05-03',
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
            "condition_date_diff_absolute": False,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })

        # 2017-05-03 - 2017-05-01 = 2 days
        self.assertTrue(condition.check(rec))

        # 2017-05-03 - 2017-05-13 != 2 days
        rec.date_start = '2017-05-13'
        self.assertFalse(condition.check(rec))

        # 2017-05-03 - 2017-05-05 = -2 days
        self.assertFalse(condition.check(rec))

        # abs(2017-05-03 - 2017-05-05) = 2 days
        condition.condition_date_diff_absolute = True
        rec.date_start = '2017-05-05'
        self.assertTrue(condition.check(rec))

    def test_50_condition_date_diff_current_time(self):
        condition = self._create_condition({
            "condition_date_diff_date_start_type": 'field',
            "condition_date_diff_date_start_field": self.test_field_start_date.id,  # noqa
            "condition_date_diff_date_end_type": 'now',
            "condition_date_diff_operator": '=',
            "condition_date_diff_uom": 'days',
            "condition_date_diff_value": 2,
            "condition_date_diff_absolute": False,
        })

        rec = self.TestModel.create({
            'date_start': '2017-05-01',
            'date_end': '2017-05-10',
        })

        # 2017-05-03 - 2017-05-01 = 2 days
        with freeze_time('2017-05-03'):
            self.assertTrue(condition.check(rec))

        # 2017-05-13 - 2017-05-01 != 2 days
        with freeze_time('2017-05-13'):
            self.assertFalse(condition.check(rec))

        # Test operator <
        condition.condition_date_diff_operator = '<'
        with freeze_time('2017-05-02'):  # 2017-05-02 - 2017-05-01 < 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-03'):  # ! (2017-05-03 - 2017-05-01 < 2 days)
            self.assertFalse(condition.check(rec))

        # Test operator <=
        condition.condition_date_diff_operator = '<='
        with freeze_time('2017-05-02'):  # 2017-05-02 - 2017-05-01 <= 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-03'):  # 2017-05-03 - 2017-05-01 <= 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-04'):  # !(2017-05-04 - 2017-05-01 <= 2 days)
            self.assertFalse(condition.check(rec))

        # Test operator >
        condition.condition_date_diff_operator = '>'
        with freeze_time('2017-05-04'):  # 2017-05-04 - 2017-05-01 > 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-03'):  # ! (2017-05-03 - 2017-05-01 > 2 days)
            self.assertFalse(condition.check(rec))

        # Test operator >=
        condition.condition_date_diff_operator = '>='
        with freeze_time('2017-05-04'):  # 2017-05-04 - 2017-05-01 >= 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-03'):  # 2017-05-03 - 2017-05-01 >= 2 days
            self.assertTrue(condition.check(rec))

        with freeze_time('2017-05-02'):  # !(2017-05-02 - 2017-05-01 >= 2 days)
            self.assertFalse(condition.check(rec))
