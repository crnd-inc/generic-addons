from odoo.tests.common import SavepointCase


class TestGenericLocationAddress(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGenericLocationAddress, cls).setUpClass()
        cls.location_country = cls.env.ref(
            'generic_location_address.demo_location_country_us')
        cls.location_state = cls.env.ref(
            'generic_location_address.demo_location_state_us_ny')
        cls.location_city = cls.env.ref(
            'generic_location_address.demo_location_city_us_ny_buffalo')

    def test_parent_state_no_use_parent(self):
        self.assertTrue(self.location_state.state_id)
        self.assertTrue(self.location_state.country_id)
        sublocation = self.env['generic.location'].create({
            'name': 'test sublocation',
            'parent_id': self.location_state.id,
            'state_id_use_parent': False,
            'country_id_use_parent': False,
        })
        self.assertFalse(sublocation.state_id)
        self.assertFalse(sublocation._state_id)

        # Default country is set based on user's country
        self.assertEqual(
            sublocation.country_id, self.env.user.company_id.country_id)
        self.assertEqual(
            sublocation._country_id, self.env.user.company_id.country_id)

    def test_parent_state_use_parent(self):
        self.assertTrue(self.location_state.state_id)
        self.assertTrue(self.location_state.country_id)
        sublocation = self.env['generic.location'].create({
            'name': 'test sublocation',
            'parent_id': self.location_state.id,
            'state_id_use_parent': True,
            'country_id_use_parent': True,
        })
        self.assertEqual(sublocation.state_id,
                         self.location_state.state_id)
        self.assertFalse(sublocation._state_id)
        self.assertEqual(sublocation.country_id,
                         self.location_country.country_id)
        self.assertFalse(sublocation._country_id)

    def test_parent_onchange(self):
        sublocation = self.env['generic.location'].new({
            'name': 'test sublocation',
        })
        self.assertFalse(sublocation.street_use_parent)
        self.assertFalse(sublocation.street2_use_parent)
        self.assertFalse(sublocation.zip_use_parent)
        self.assertFalse(sublocation.city_use_parent)
        self.assertFalse(sublocation.state_id_use_parent)
        self.assertFalse(sublocation.country_id_use_parent)

        sublocation.onchange_parent()
        self.assertFalse(sublocation.street_use_parent)
        self.assertFalse(sublocation.street2_use_parent)
        self.assertFalse(sublocation.zip_use_parent)
        self.assertFalse(sublocation.city_use_parent)
        self.assertFalse(sublocation.state_id_use_parent)
        self.assertFalse(sublocation.country_id_use_parent)

        sublocation.parent_id = self.location_state
        sublocation.onchange_parent()
        self.assertTrue(sublocation.street_use_parent)
        self.assertTrue(sublocation.street2_use_parent)
        self.assertTrue(sublocation.zip_use_parent)
        self.assertTrue(sublocation.city_use_parent)
        self.assertTrue(sublocation.state_id_use_parent)
        self.assertTrue(sublocation.country_id_use_parent)
