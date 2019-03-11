from odoo.tests.common import SavepointCase


class TestGenericLocation(SavepointCase):

    def test_create_location(self):
        simplelocation = self.env.ref(
            'generic_location.' 'simple_parent_location_4')
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
