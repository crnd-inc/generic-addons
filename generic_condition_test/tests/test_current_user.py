from odoo.tests.common import SavepointCase


class TestConditionCurrentUser(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestConditionCurrentUser, cls).setUpClass()
        cls.test_model = cls.env['ir.model'].search(
            [('model', '=', 'test.generic.condition.test.model')])

        cls.TestModel = cls.env[cls.test_model.model]
        cls.ResUsers = cls.env['res.users']

        cls.Condition = cls.env['generic.condition']
        cls.condition_data = {
            "name": 'Current user condition',
            "model_id": cls.test_model.id,
            "type": 'current_user',
        }

    def _create_condition(self, field_name):
        """ Simple helper to create new condition with some predefined values
        """
        field = self.test_model.field_id.filtered(
            lambda r: r.name == field_name)

        condition_data = self.condition_data.copy()
        condition_data.update({
            'condition_user_check_type': 'field',
            'condition_user_user_field_id': field.id,
        })
        return self.Condition.create(condition_data)

    def _create_record(self, **field_vals):
        """ Generate test record
        """
        return self.TestModel.create(field_vals)

    def test_10_current_user__field__m2o(self):
        condition = self._create_condition('user_m2o')
        user = self.env.ref('base.user_demo')

        rec = self._create_record(user_m2o=False)
        self.assertFalse(condition.check(rec))
        rec = self._create_record(user_m2o=user.id)
        self.assertFalse(condition.check(rec))
        self.assertTrue(condition.with_user(user).check(rec))

    def test_15_current_user__field__m2m(self):
        condition = self._create_condition('user_m2m')
        user = self.env.ref('base.user_demo')

        rec = self._create_record(user_m2m=False)
        self.assertFalse(condition.check(rec))

        users = [self.env.user.id, user.id]

        rec = self._create_record(
            user_m2m=[(6, 0, users)])
        self.assertTrue(condition.with_user(user).check(rec))

    def test_20_current_user__one_of(self):
        user = self.env.ref('base.user_demo')
        user_root = self.env.ref('base.user_root')
        condition = self.Condition.create(dict(
            self.condition_data,
            condition_user_check_type='one_of',
            condition_user_one_of_user_ids=[(6, 0, [user.id])],
        ))
        self.assertEqual(self.env.user, user_root)

        rec = self._create_record(user_m2o=False)

        # Root user is not demo user
        self.assertFalse(condition.check(rec))
        self.assertTrue(condition.with_user(user).check(rec))

    def test_25_current_user__checks(self):
        user = self.env.ref('base.user_demo')
        user_portal = self.env.ref('base.demo_user0')
        user_root = self.env.ref('base.user_root')
        condition_user_internal = self.env.ref(
            'generic_condition.condition_user_is_internal')
        condition = self.Condition.create(dict(
            self.condition_data,
            condition_user_check_type='checks',
            condition_user_checks_condition_ids=[
                (6, 0, [condition_user_internal.id])],
        ))
        self.assertEqual(self.env.user, user_root)

        rec = self._create_record(user_m2o=False)

        # Root user is not demo user
        self.assertTrue(condition.check(rec))
        self.assertFalse(condition.with_user(user_portal).check(rec))
        self.assertTrue(condition.with_user(user).check(rec))
