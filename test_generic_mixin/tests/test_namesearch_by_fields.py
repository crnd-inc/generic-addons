from odoo.tests.common import SavepointCase


class NamesearchByFieldsTest(SavepointCase):

    def test_name_search_by_fields(self):
        Model = self.env['test.mixin.name.search.by.fields']
        Model.create([
            {
                'name': 'Alpha',
                'code': 'a1',
                'test_field': 'test-z',
            },
            {
                'name': 'Beta',
                'code': 'b1',
                'test_field': 'test-y',
            },
            {
                'name': 'Gamma',
                'code': 'g1',
                'test_field': 'test-x',
            },
        ])

        self.assertEqual(len(Model.name_search('alpha')), 1)
        self.assertEqual(Model.name_search('alpha')[0][1], "Alpha")
        self.assertEqual(len(Model.name_search('a1')), 1)
        self.assertEqual(Model.name_search('a1')[0][1], "Alpha")
        self.assertEqual(len(Model.name_search('test-z')), 0)

        self.assertEqual(len(Model.name_search('Beta')), 1)
        self.assertEqual(Model.name_search('Beta')[0][1], "Beta")
        self.assertEqual(len(Model.name_search('b1')), 1)
        self.assertEqual(Model.name_search('b1')[0][1], "Beta")
        self.assertEqual(len(Model.name_search('test-x')), 0)
