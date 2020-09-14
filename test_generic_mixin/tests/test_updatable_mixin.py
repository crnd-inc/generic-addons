from odoo.tests.common import SavepointCase


class UpdatableMixinTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(UpdatableMixinTest, cls).setUpClass()

    def test_track_changes(self):
        # pylint: disable=too-many-statements
        Model = self.env['test.generic.mixin.track.changes.model']

        r1 = self.env.ref('test_generic_mixin.demo_tc_1')
        self.assertTrue(r1.ir_model_data_no_update)
        self.assertTrue(r1.ir_model_data_id.noupdate)
        self.assertEqual(
            r1.ir_model_data_xmlid, 'test_generic_mixin.demo_tc_1')

        r1.ir_model_data_no_update = False
        self.assertFalse(r1.ir_model_data_no_update)
        self.assertFalse(r1.ir_model_data_id.noupdate)

        r2 = self.env.ref('test_generic_mixin.demo_tc_2')

        recs = Model.search([('ir_model_data_no_update', '=', True)])
        self.assertEqual(recs, r2)

        recs = Model.search([('ir_model_data_no_update', '=', False)])
        self.assertEqual(recs, r1)

        r1.ir_model_data_no_update = True
        self.assertTrue(r1.ir_model_data_no_update)
        self.assertTrue(r1.ir_model_data_id.noupdate)

        recs = Model.search([('ir_model_data_no_update', '=', True)])
        self.assertEqual(set(recs.ids), set([r1.id, r2.id]))
