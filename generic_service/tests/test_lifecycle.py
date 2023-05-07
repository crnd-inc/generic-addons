import logging

from odoo import exceptions
from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin
)

_logger = logging.getLogger(__name__)


class TestGenericServiceLevel(ReduceLoggingMixin, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestGenericServiceLevel, cls).setUpClass()

        cls.test_service = cls.env['generic.service'].create({
            'name': 'Test Service (Auto 42)',
            'code': 'test-service-auto-42',
        })

    def test_lifecycle_base_flow(self):
        self.assertEqual(self.test_service.lifecycle_state, 'draft')
        self.assertTrue(self.test_service.lifecycle_date_created)
        self.assertFalse(self.test_service.lifecycle_date_activated)
        self.assertFalse(self.test_service.lifecycle_date_obsolete)
        self.assertFalse(self.test_service.lifecycle_date_archived)
        self.assertTrue(self.test_service.active)

        self.test_service.action_lifecycle_state__activate()

        self.assertEqual(self.test_service.lifecycle_state, 'active')
        self.assertTrue(self.test_service.lifecycle_date_created)
        self.assertTrue(self.test_service.lifecycle_date_activated)
        self.assertFalse(self.test_service.lifecycle_date_obsolete)
        self.assertFalse(self.test_service.lifecycle_date_archived)
        self.assertTrue(self.test_service.active)

        self.test_service.action_lifecycle_state__obsolete()

        self.assertEqual(self.test_service.lifecycle_state, 'obsolete')
        self.assertTrue(self.test_service.lifecycle_date_created)
        self.assertTrue(self.test_service.lifecycle_date_activated)
        self.assertTrue(self.test_service.lifecycle_date_obsolete)
        self.assertFalse(self.test_service.lifecycle_date_archived)
        self.assertTrue(self.test_service.active)

        self.test_service.action_lifecycle_state__archive()

        self.assertEqual(self.test_service.lifecycle_state, 'archived')
        self.assertTrue(self.test_service.lifecycle_date_created)
        self.assertTrue(self.test_service.lifecycle_date_activated)
        self.assertTrue(self.test_service.lifecycle_date_obsolete)
        self.assertTrue(self.test_service.lifecycle_date_archived)
        self.assertFalse(self.test_service.active)

    def test_lifecycle_allow_delete_draft(self):
        self.assertEqual(self.test_service.lifecycle_state, 'draft')

        # No errors have to be raised
        self.test_service.unlink()

    def test_lifecycle_deny_delete_active(self):
        self.test_service.lifecycle_state = 'active'
        self.assertEqual(self.test_service.lifecycle_state, 'active')

        with self.assertRaises(exceptions.UserError):
            # No errors have to be raised
            self.test_service.unlink()

    def test_lifecycle_deny_deactivate(self):
        self.test_service.lifecycle_state = 'active'
        self.assertEqual(self.test_service.lifecycle_state, 'active')

        with self.assertRaises(exceptions.ValidationError):
            self.test_service.lifecycle_state = 'draft'
