from odoo.tests.common import SavepointCase


class ProxyMethodsMixinTest(SavepointCase):

    def test_proxy_method_single_rec(self):
        rec1 = self.env['test.proxy.method.my.specific.model.1'].create({
            'specific_field_1': 'test-f1',
            'base_field': 'test'
        })
        self.assertEqual(rec1.specific_field_1, 'test-f1')
        self.assertEqual(rec1.base_field, 'test')

        rec1.action_my_action()

        self.assertEqual(rec1.specific_field_1, 'test-f1')
        self.assertEqual(rec1.base_field, 'action-done')

        rec1 = self.env['test.proxy.method.my.specific.model.2'].create({
            'specific_field_2': 'test-f2',
            'base_field': 'test-2'
        })
        self.assertEqual(rec1.specific_field_2, 'test-f2')
        self.assertEqual(rec1.base_field, 'test-2')

        rec1.action_my_action()

        self.assertEqual(rec1.specific_field_2, 'test-f2')
        self.assertEqual(rec1.base_field, 'action-done')

    def test_proxy_method_multi_rec(self):
        rec1 = self.env['test.proxy.method.my.specific.model.1'].create({
            'specific_field_1': 'test-f1-1',
            'base_field': 'test-1'
        })
        rec2 = self.env['test.proxy.method.my.specific.model.1'].create({
            'specific_field_1': 'test-f1-2',
            'base_field': 'test-2'
        })
        rec3 = self.env['test.proxy.method.my.specific.model.1'].create({
            'specific_field_1': 'test-f1-3',
            'base_field': 'test-3'
        })
        recs = (rec1 + rec2 + rec3)

        self.assertEqual(rec1.specific_field_1, 'test-f1-1')
        self.assertEqual(rec1.base_field, 'test-1')

        self.assertEqual(rec2.specific_field_1, 'test-f1-2')
        self.assertEqual(rec2.base_field, 'test-2')

        self.assertEqual(rec3.specific_field_1, 'test-f1-3')
        self.assertEqual(rec3.base_field, 'test-3')

        recs.action_my_action_multi()

        self.assertEqual(rec1.specific_field_1, 'test-f1-1')
        self.assertEqual(rec1.base_field, 'action-done-test-1')

        self.assertEqual(rec2.specific_field_1, 'test-f1-2')
        self.assertEqual(rec2.base_field, 'action-done-test-2')

        self.assertEqual(rec3.specific_field_1, 'test-f1-3')
        self.assertEqual(rec3.base_field, 'action-done-test-3')
