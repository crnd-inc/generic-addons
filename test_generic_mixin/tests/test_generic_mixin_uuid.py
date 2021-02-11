import uuid
from odoo import fields
from odoo.tests.common import SavepointCase


class NameBySequenceTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(NameBySequenceTest, cls).setUpClass()

    def test_generic_mixin_uuid_1(self):
        Model = self.env['test.generic.mixin.uuid.standard']
        self.assertIn('uuid', Model._fields)
        self.assertIsInstance(Model._fields['uuid'], fields.Char)

        rec = Model.create({'name': 'New'})

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        uuid.UUID(rec.uuid)
