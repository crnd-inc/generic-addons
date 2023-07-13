from odoo.tests.common import SavepointCase


class TestGenericResourceSearch(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestGenericResourceSearch, cls).setUpClass()

        cls.demo_model = cls.env['test.generic.resource.name.search']

        cls.record_printer_i255 = cls.env.ref(
            'test_generic_resource_search.demo_record_printer_i255_resource')
        cls.record_printer_i123 = cls.env.ref(
            'test_generic_resource_search.demo_record_printer_i123_resource')
        cls.record_printer_i569 = cls.env.ref(
            'test_generic_resource_search.demo_record_printer_i569_resource')
        cls.record_desktop = cls.env.ref(
            'test_generic_resource_search.demo_record_desktop_resource')
        cls.record_notebook = cls.env.ref(
            'test_generic_resource_search.demo_record_notebook_resource')

    def test_search_resource_id(self):
        result = self.demo_model.search([('resource_id', 'ilike', 'i255')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, self.record_printer_i255.id)

        result = self.demo_model.search([('resource_id', 'ilike', 'i123')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, self.record_printer_i123.id)

        result = self.demo_model.search([('resource_id', 'ilike', 'i569')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, self.record_printer_i569.id)

        result = self.demo_model.search([('resource_id', 'ilike', 'desktop')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, self.record_desktop.id)

        result = self.demo_model.search([('resource_id', 'ilike', 'notebook')])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.id, self.record_notebook.id)
