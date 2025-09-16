import uuid
import logging

from odoo import fields
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class UUIDMixinTest(TransactionCase):

    def test_generic_mixin_uuid_1(self):
        Model = self.env['test.generic.mixin.uuid.standard']
        self.assertIn('x_uuid', Model._fields)
        self.assertIsInstance(Model._fields['x_uuid'], fields.Char)

        rec = Model.create({'name': 'New'})

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        uuid.UUID(rec.x_uuid)

        self.assertEqual(rec.id, Model.get_by_uuid(rec.x_uuid).id)

    def test_generic_mixin_uuid_2(self):
        Model = self.env['test.generic.mixin.uuid.named.field']
        self.assertIn('x_myuuid', Model._fields)
        self.assertIsInstance(Model._fields['x_myuuid'], fields.Char)

        rec = Model.create({'name': 'New'})

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        _logger.info('U: %s', rec.x_myuuid)
        uuid.UUID(rec.x_myuuid)

        self.assertEqual(rec.id, Model.get_by_uuid(rec.x_myuuid).id)

    def test_generic_mixin_uuid_3(self):
        Model = self.env['test.generic.mixin.uuid.named.field']
        self.assertIn('x_myuuid', Model._fields)
        self.assertIsInstance(Model._fields['x_myuuid'], fields.Char)

        rec = Model.create({
            'name': 'New',
            'x_myuuid': str(uuid.uuid4())
        })

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        _logger.info('U: %s', rec.x_myuuid)
        uuid.UUID(rec.x_myuuid)

        self.assertEqual(rec.id, Model.get_by_uuid(rec.x_myuuid).id)

    def test_generic_mixin_uuid_4(self):
        Model = self.env['test.generic.mixin.uuid.named.field']
        self.assertIn('x_myuuid', Model._fields)
        self.assertIsInstance(Model._fields['x_myuuid'], fields.Char)

        u = str(uuid.uuid4())
        rec = Model.create_or_update_by_uuid(u, {
            'name': 'New',
        })
        self.assertEqual(rec.x_myuuid, u)
        self.assertEqual(rec.name, 'New')

        rec1 = Model.create_or_update_by_uuid(u, {
            'name': 'Updated',
        })
        self.assertEqual(rec.x_myuuid, u)
        self.assertEqual(rec.name, 'Updated')
        self.assertEqual(rec.id, rec1.id)
