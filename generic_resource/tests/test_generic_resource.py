from odoo import exceptions
from odoo.tools.misc import mute_logger
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin
)


@tagged('post_install', '-at_install')
class TestResource(ReduceLoggingMixin, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestResource, cls).setUpClass()

        cls.resource = cls.env['generic.resource.simple'].create({
            'name': 'test-resource'
        })
        cls.resource_type = cls.env.ref(
            'generic_resource.generic_resource_type_default')

    def test_create_resource(self):

        self.assertTrue(self.resource.resource_id,
                        'Model must have bound resource')

        resource = self.resource.resource_id
        self.assertTrue(resource.res_type_id, 'Resource must have a type')
        self.assertEqual(resource.res_model, self.resource._name,
                         'Resource model must be the same as test model')
        self.assertTrue(resource.res_id,
                        'Resource must have an id of instance')

        resource_model = self.env[resource.res_model].browse(resource.res_id)

        self.assertEqual(resource_model, self.resource,
                         'Resource model must be the same as test model')

        self.assertTrue(resource.display_name.startswith('test-resource [SR'))

    def test_create_resource_res_id(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env['generic.resource'].create({
                'res_id': 42,
                'res_type_id': self.resource_type.id
            })

    def test_unlink(self):
        # Get related resource
        gen_resource = self.resource.resource_id
        # Delete test resource
        self.resource.unlink()
        self.assertFalse(self.resource.exists(), "Resource should be deleted!")
        self.assertFalse(
            gen_resource.exists(),
            'Related generic resource should be deleted!')

    def test_copy(self):
        # Copy resource
        new_resource = self.resource.copy({'name': 'test 42'})

        # Test copied resource
        self.assertNotEqual(
            new_resource.resource_id, self.resource.resource_id)
        self.assertEqual(new_resource.name, 'test 42')
        self.assertEqual(self.resource.name, 'test-resource')

    def test_update_res_id(self):
        with self.assertRaises(exceptions.ValidationError):
            self.resource.res_id = 78

    def test_update_resource_id(self):
        resource_other = self.env['generic.resource.simple'].create({
            'name': 'test-other-resource',
        })
        self.assertNotEqual(
            self.resource.resource_id, resource_other.resource_id)

        gresource = self.resource.resource_id

        with mute_logger(
                "odoo.addons.generic_mixin.models.generic_mixin_guard_fields"):
            self.resource.write({
                'resource_id': resource_other.resource_id.id,
            })

        # Ensure resource_id was not changed
        self.assertEqual(self.resource.resource_id, gresource)
        self.assertNotEqual(
            self.resource.resource_id, resource_other.resource_id)
