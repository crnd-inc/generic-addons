from odoo import fields
from odoo.tests.common import SavepointCase


class NameBySequenceTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(NameBySequenceTest, cls).setUpClass()

        cls.sequence = cls.env['ir.sequence'].browse
        cls.test_sequence = cls.env['ir.sequence'].search([
            ('code', '=', 'generic.mixin.test.name.by.sequence.name'),
        ], order='company_id', limit=1)

    def _get_next_sequence_number(self):
        self.test_sequence.refresh()
        return self.test_sequence.read(
            ['number_next_actual']
        )[0]['number_next_actual']

    def test_name_by_sequence_no_field_default_behavior(self):
        Model = self.env['test.generic.mixin.name.by.sequence.nf']
        self.assertIn('name', Model._fields)
        self.assertIsInstance(Model._fields['name'], fields.Char)
        self.assertEqual(Model._fields['name'].string, 'Name')

        next_number = self._get_next_sequence_number()
        rec = Model.create({})
        self.assertEqual(rec.name, 'GMTNBSN%s' % next_number)

        next_number = self._get_next_sequence_number()
        rec = Model.create({'name': 'New'})
        self.assertEqual(rec.name, 'GMTNBSN%s' % next_number)

        rec = Model.create({'name': 'Custom name'})
        self.assertEqual(rec.name, 'Custom name')

    def test_name_by_sequence_custom_field(self):
        Model = self.env['test.generic.mixin.name.by.sequence.cf']
        self.assertIn('my_name', Model._fields)
        self.assertNotIn('name', Model._fields)
        self.assertIsInstance(Model._fields['my_name'], fields.Char)
        self.assertEqual(Model._fields['my_name'].string, 'My Name')

        next_number = self._get_next_sequence_number()
        rec = Model.create({})
        self.assertEqual(rec.my_name, 'GMTNBSN%s' % next_number)

        next_number = self._get_next_sequence_number()
        rec = Model.create({'my_name': 'New'})
        self.assertEqual(rec.my_name, 'GMTNBSN%s' % next_number)

        rec = Model.create({'my_name': 'Custom name'})
        self.assertEqual(rec.my_name, 'Custom name')

    def test_name_by_sequence_custom_field_custom_name(self):
        Model = self.env['test.generic.mixin.name.by.sequence.cfcn']
        self.assertIn('my_name', Model._fields)
        self.assertNotIn('name', Model._fields)
        self.assertIsInstance(Model._fields['my_name'], fields.Char)
        self.assertEqual(Model._fields['my_name'].string, 'My Name Field')

        next_number = self._get_next_sequence_number()
        rec = Model.create({})
        self.assertEqual(rec.my_name, 'GMTNBSN%s' % next_number)

        next_number = self._get_next_sequence_number()
        rec = Model.create({'my_name': 'New'})
        self.assertEqual(rec.my_name, 'GMTNBSN%s' % next_number)

        rec = Model.create({'my_name': 'Custom name'})
        self.assertEqual(rec.my_name, 'Custom name')

    def test_name_by_sequence_no_sequence(self):
        Model = self.env['test.generic.mixin.name.by.sequence.ns']
        self.assertIn('name', Model._fields)
        self.assertIsInstance(Model._fields['name'], fields.Char)
        self.assertEqual(Model._fields['name'].string, 'Name')

        # Field was added, so its default value was used
        rec = Model.create({})
        self.assertEqual(rec.name, 'New')

        rec = Model.create({'name': 'Custom value'})
        self.assertEqual(rec.name, 'Custom value')

    def test_name_by_sequence_no_sequence_no_auto_field(self):
        Model = self.env['test.generic.mixin.name.by.sequence.nsnf']
        self.assertNotIn('name', Model._fields)

        # Ensure no errors raised
        rec = Model.create({})
        self.assertTrue(rec)

    def test_name_by_sequence_no_sequence_no_auto_field_no_sequence(self):
        Model = self.env['test.generic.mixin.name.by.sequence.nsnfcf']
        self.assertIn('name', Model._fields)

        rec = Model.create({})
        self.assertEqual(rec.name, 'New')

        rec = Model.create({'name': 'Custom value'})
        self.assertEqual(rec.name, 'Custom value')

    def test_name_by_sequence_no_auto_field_custom_field(self):
        Model = self.env['test.generic.mixin.name.by.sequence.nfcf']
        self.assertIn('name', Model._fields)
        self.assertIsInstance(Model._fields['name'], fields.Char)
        self.assertEqual(Model._fields['name'].string, 'Name')

        next_number = self._get_next_sequence_number()
        rec = Model.create({})
        self.assertEqual(rec.name, 'GMTNBSN%s' % next_number)

        next_number = self._get_next_sequence_number()
        rec = Model.create({'name': 'New'})
        self.assertEqual(rec.name, 'GMTNBSN%s' % next_number)

        rec = Model.create({'name': 'Custom name'})
        self.assertEqual(rec.name, 'Custom name')
