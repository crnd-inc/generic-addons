from odoo import exceptions
from odoo.tools.misc import mute_logger
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin
)


@tagged('post_install', '-at_install')
class TestDelegation(ReduceLoggingMixin, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_implementation_multi_interfaces(self):

        rec = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })
        self.assertEqual(rec.interface_1_id.interface_1_impl_id, rec.id)
        self.assertEqual(rec.interface_2_id.interface_2_impl_id, rec.id)
        self.assertEqual(
            rec.interface_1_impl_model,
            'test.generic.mixin.multi.interface.impl')
        self.assertEqual(
            rec.interface_2_impl_model,
            'test.generic.mixin.multi.interface.impl')

    def test_create_with_implementation_id(self):
        rec = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })

        # Try to rewrite implementation_id on create
        rec2 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'interface_1_impl_id': rec.id,
            'name': "test",
        })
        self.assertNotEqual(rec2.interface_1_id.interface_1_impl_id, rec.id)
        self.assertEqual(rec2.interface_1_id.interface_1_impl_id, rec2.id)

    def test_unlink(self):
        rec = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })

        # Keep references to interfaces
        interface_1 = rec.interface_1_id
        interface_2 = rec.interface_2_id

        # Delete implementation
        rec.unlink()

        # Ensure interfaces deleted
        self.assertFalse(rec.exists())
        self.assertFalse(interface_1.exists())
        self.assertFalse(interface_2.exists())

    def test_update_implementation_id(self):
        rec1 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })
        rec2 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'One',
            'interface_2_test_field_1': 'Two',
            'name': "test",
        })

        with self.assertRaises(exceptions.ValidationError):
            rec1.interface_1_id.interface_1_impl_id = rec2.id

    def test_update_interface_id(self):
        rec1 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })
        rec2 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'One',
            'interface_2_test_field_1': 'Two',
            'name': "test",
        })

        # Try to change interface of rec1
        old_interface = rec1.interface_1_id
        with mute_logger(
                "odoo.addons.generic_mixin.models.generic_mixin_guard_fields"):
            rec1.write({
                'interface_1_id': rec2.interface_1_id,
            })

        # Ensure interface was not changed
        self.assertEqual(rec1.interface_1_id, old_interface)
        self.assertNotEqual(
            rec1.interface_1_id, rec2.interface_1_id)

    def test_copy(self):
        rec1 = self.env['test.generic.mixin.multi.interface.impl'].create({
            'interface_1_test_field_1': 'Hello',
            'interface_2_test_field_1': 'World',
            'name': "test",
        })

        # Try to copy created record
        rec2 = rec1.copy({
            'name': "test-42",
            'interface_2_test_field_1': 'Space',
        })
        self.assertNotEqual(rec2.interface_1_id, rec1.interface_1_id)
        self.assertNotEqual(rec2.interface_2_id, rec1.interface_2_id)
        self.assertEqual(rec2.name, 'test-42')
        self.assertEqual(rec2.interface_1_test_field_1, 'Hello')
        self.assertEqual(rec2.interface_2_test_field_1, 'Space')
