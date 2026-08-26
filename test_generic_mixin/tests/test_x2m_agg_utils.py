from odoo.tests.common import TransactionCase

from odoo.addons.generic_mixin.tools.x2m_agg_utils import (
    read_counts_for,
    read_counts_for_o2m,
)


class TestX2mAggUtils(TransactionCase):
    """Counts of related records, keyed by the value looked up.

    Rows without related records are absent from the mapping, not zero.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Parent = cls.env['test.generic.mixin.x2m.agg.parent']
        cls.Child = cls.env['test.generic.mixin.x2m.agg.child']

        cls.parent1 = cls.Parent.create({'name': 'P1', 'code': 'c1'})
        cls.parent2 = cls.Parent.create({'name': 'P2', 'code': 'c2'})
        cls.parent_empty = cls.Parent.create({'name': 'P3', 'code': 'c3'})

        cls.Child.create([
            {'name': 'a', 'parent_id': cls.parent1.id, 'parent_code': 'c1'},
            {'name': 'b', 'parent_id': cls.parent1.id, 'parent_code': 'c1'},
            {'name': 'c', 'parent_id': cls.parent1.id, 'parent_code': 'c1'},
            {'name': 'd', 'parent_id': cls.parent2.id, 'parent_code': 'c2'},
        ])

    def test_counts_per_record(self):
        counts = read_counts_for_o2m(
            records=self.parent1 | self.parent2, field_name='child_ids')

        self.assertEqual(counts, {self.parent1.id: 3, self.parent2.id: 1})

    def test_record_without_children_is_absent(self):
        """Callers use ``.get(record.id, 0)``."""
        counts = read_counts_for_o2m(
            records=self.parent1 | self.parent_empty, field_name='child_ids')

        self.assertEqual(counts, {self.parent1.id: 3})
        self.assertNotIn(self.parent_empty.id, counts)

    def test_keys_are_ids_and_values_are_ints(self):
        """Keys are plain ids, not recordsets or (id, name) pairs."""
        counts = read_counts_for_o2m(
            records=self.parent1, field_name='child_ids')

        (key, value), = counts.items()
        self.assertIsInstance(key, int)
        self.assertIsInstance(value, int)

    def test_empty_recordset_returns_empty_mapping(self):
        counts = read_counts_for_o2m(
            records=self.Parent.browse(), field_name='child_ids')

        self.assertEqual(counts, {})

    def test_unsaved_record_returns_empty_mapping(self):
        counts = read_counts_for_o2m(
            records=self.Parent.new({'name': 'draft'}),
            field_name='child_ids')

        self.assertEqual(counts, {})

    def test_extra_domain_narrows_the_count(self):
        self.Child.search([('name', '=', 'a')]).write({'active': False})

        counts = read_counts_for_o2m(
            records=self.parent1, field_name='child_ids',
            domain=[('active', '=', True)])

        self.assertEqual(counts, {self.parent1.id: 2})

    def test_sudo_is_accepted(self):
        counts = read_counts_for_o2m(
            records=self.parent1, field_name='child_ids', sudo=True)

        self.assertEqual(counts, {self.parent1.id: 3})

    def test_non_one2many_field_is_rejected(self):
        with self.assertRaises(ValueError):
            read_counts_for_o2m(
                records=self.parent1, field_name='other_ids')

        with self.assertRaises(ValueError):
            read_counts_for_o2m(
                records=self.parent1, field_name='name')

    def test_read_counts_for_with_non_id_value_field(self):
        """Any field of the records may be matched against any field of
        the related model."""
        counts = read_counts_for(
            records=self.parent1 | self.parent2,
            related_model='test.generic.mixin.x2m.agg.child',
            search_field='parent_code',
            value_field='code')

        self.assertEqual(counts, {'c1': 3, 'c2': 1})

    def test_counts_ignore_unrelated_records(self):
        other = self.Parent.create({'name': 'P4', 'code': 'c4'})
        self.Child.create({'name': 'z', 'parent_id': other.id})

        counts = read_counts_for_o2m(
            records=self.parent1, field_name='child_ids')

        self.assertEqual(counts, {self.parent1.id: 3})
