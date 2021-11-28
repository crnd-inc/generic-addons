import uuid
import logging

from odoo import fields
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class UUIDMixinTest(TransactionCase):

    def test_generic_mixin_uuid_1(self):
        Model = self.env['test.generic.mixin.uuid.standard']
        self.assertIn('uuid', Model._fields)
        self.assertIsInstance(Model._fields['uuid'], fields.Char)

        rec = Model.create({'name': 'New'})

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        uuid.UUID(rec.uuid)

    def test_generic_mixin_uuid_2(self):
        Model = self.env['test.generic.mixin.uuid.named.field']
        self.assertIn('myuuid', Model._fields)
        self.assertIsInstance(Model._fields['myuuid'], fields.Char)

        rec = Model.create({'name': 'New'})

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        _logger.info('U: %s', rec.myuuid)
        uuid.UUID(rec.myuuid)

    def test_generic_mixin_uuid_3(self):
        Model = self.env['test.generic.mixin.uuid.named.field']
        self.assertIn('myuuid', Model._fields)
        self.assertIsInstance(Model._fields['myuuid'], fields.Char)

        rec = Model.create({
            'name': 'New',
            'myuuid': str(uuid.uuid4())
        })

        # Test that creation of UUID obj will not raise error, thus it seems
        # that uuid field was generated in right way.
        # If UUID receive wrong param, then it will raise ValueError
        _logger.info('U: %s', rec.myuuid)
        uuid.UUID(rec.myuuid)
