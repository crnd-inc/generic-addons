from odoo import exceptions
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install')
class TestCustomResource(TransactionCase):

    def setUp(self):
        super(TestCustomResource, self).setUp()

        self.env['ir.ui.view'].search([
            ('model', 'not in', list(self.registry.models))
        ]).write({
            'active': False,
        })

    def test_create_custom_resource(self):
        # Create custom resource model
        res_model = self.env['ir.model'].create({
            'name': 'Test Custom Resource',
            'model': 'x_test_custom_resource',
            'is_generic_resource': True,
        })

        self.assertTrue(res_model.is_generic_resource)
        self.assertTrue(res_model.resource_type_id)
        self.assertEqual(res_model.resource_type_id.name, res_model.name)

        # Ensure resource type created for that model
        res_type = res_model.resource_type_id
        self.assertTrue(res_type.exists())

        # Create new  resource
        resource = self.env['x_test_custom_resource'].create({
            'x_name': 'Test',
        })
        self.assertEqual(resource.resource_id.res_type_id, res_type)

        # Try to set is_generic_resource to False
        with self.assertRaises(exceptions.UserError):
            res_model.write({
                'is_generic_resource': False,
            })

        # Delete created model
        res_model.unlink()

        # Ensure type removed
        self.assertFalse(res_type.exists())

    def test_create_custom_resource_change(self):
        # Create custom resource model
        res_model = self.env['ir.model'].create({
            'name': 'Test Custom Resource',
            'model': 'x_test_custom_resource',
        })

        self.assertFalse(res_model.is_generic_resource)
        self.assertFalse(res_model.resource_type_id)

        # Change model to resource
        res_model.is_generic_resource = True

        # Ensure model converted to resource type
        self.assertTrue(res_model.is_generic_resource)
        self.assertTrue(res_model.resource_type_id)
        self.assertEqual(res_model.resource_type_id.name, res_model.name)

        # Ensure resource type created for that model
        res_type = res_model.resource_type_id
        self.assertTrue(res_type.exists())

        # Create new  resource
        resource = self.env['x_test_custom_resource'].create({
            'x_name': 'Test',
        })
        self.assertEqual(resource.resource_id.res_type_id, res_type)

        # Delete created model
        res_model.unlink()

        # Ensure type removed
        self.assertFalse(res_type.exists())
