from odoo.tests.common import TransactionCase


class TestGenericResourceMixinInvNumber(TransactionCase):

    def test_create_method(self):

        SimpleResource = self.env['generic.resource.simple']
        category = self.env.ref('generic_resource.'
                                'simple_resource_category_'
                                'equipment_computers_desktops')

        resource = SimpleResource.create({'name': 'test_name',
                                          'category_id': category.id})

        # test the inv_number when copying a record
        self.assertNotEqual(resource.inv_number, resource.copy().inv_number)
        # ---

        self.assertEqual(resource.inv_number[:2], 'SR')

        resource = SimpleResource.create({'name': 'test_name',
                                          'category_id': category.id,
                                          'inv_number': 'TEST-INV-NUMBER'})

        self.assertEqual(resource.inv_number, 'TEST-INV-NUMBER')
        self.assertEqual(resource.display_name, 'test_name [TEST-INV-NUMBER]')
