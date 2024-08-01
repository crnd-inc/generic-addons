from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tests.common import ReduceLoggingMixin


class TestGenericLocation(ReduceLoggingMixin, TransactionCase):

    def test_create_location(self):
        simplelocation = self.env.ref(
            'generic_location.simple_parent_location_4')
        self.assertNotEqual(simplelocation.name, simplelocation.copy().name)
        self.assertEqual(simplelocation.name, 'Hostel-3')
        self.assertEqual(simplelocation.child_ids.name, 'Room 9')
        self.assertEqual(simplelocation.child_count, 1)
        # Test action button
        testaction = simplelocation.action_button_show_sublocations()
        self.assertEqual(testaction['name'], 'Sublocations')
        self.assertEqual(testaction['res_model'], simplelocation._name)
        testdomain = testaction['domain']
        self.assertEqual(testdomain[0], ('parent_id', '=', simplelocation.id))

    def test_location_parent_names(self):
        root = self.env['generic.location'].create({
            'name': 'Root',
        })
        child = self.env['generic.location'].create({
            'name': 'Child',
            'parent_id': root.id,
        })
        self.assertEqual(child.display_name, 'Root / Child')

    def test_child_count(self):
        loc = self.env.ref(
            'generic_location.simple_location_root_1')
        self.assertEqual(loc.child_count, 2)
        self.assertEqual(loc.child_all_count, 6)

    def test_location_parent_ids(self):
        house1 = self.env.ref('generic_location.simple_parent_location_1')
        room1 = self.env.ref('generic_location.simple_location_room_1')

        self.assertEqual(room1.parent_ids, house1)

    def test_location_parent_ids_2(self):
        root = self.env['generic.location'].create({
            'name': 'Root',
        })
        house1 = self.env.ref('generic_location.simple_parent_location_1')
        room1 = self.env.ref('generic_location.simple_location_room_1')
        house1.parent_id = root

        # Without this test does not pass. It seems that parent left/right are
        # not recomputed just after write
        self.env['generic.location']._parent_store_compute()

        self.assertEqual(len(room1.parent_ids), 2)
        self.assertIn(root, room1.parent_ids)
        self.assertIn(house1, room1.parent_ids)

    def test_top_level_parent(self):
        top_level_location1 = self.env['generic.location'].create({
            'name': 'Top level location 1',
        })
        child1 = self.env['generic.location'].create({
            'name': 'Child 1',
            'parent_id': top_level_location1.id,
        })
        grand_child1 = self.env['generic.location'].create({
            'name': 'Grand Child 1',
            'parent_id': child1.id,
        })
        self.assertEqual(
            child1.top_level_parent, top_level_location1)
        self.assertEqual(
            grand_child1.top_level_parent, top_level_location1)
        self.assertEqual(
            top_level_location1.top_level_parent, top_level_location1)
