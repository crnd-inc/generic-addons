from odoo import fields
from odoo.tests import common

from odoo.addons.generic_mixin.tests.common import FindNew


class TestFindNew(common.TransactionCase):

    def test_find_new(self):
        with FindNew(self.env, "res.partner", "calendar.event") as nr:
            partner = self.env['res.partner'].create({
                'name': 'My Cooling Company',
            })
            contact = self.env['res.partner'].create({
                'name': 'John',
                'parent_id': partner.id,
            })
            meeting = self.env['calendar.event'].create({
                'name': 'Test',
                'start': fields.Datetime.from_string(
                    '2022-05-01 13:00:00'),
                'stop': fields.Datetime.from_string(
                    '2022-05-01 13:00:00'),
                'partner_ids': [(6, 0, contact.ids)],
            })

        self.assertIn(partner, nr['res.partner'])
        self.assertIn(contact, nr['res.partner'])
        self.assertEqual(len(nr['res.partner']), 2)

        self.assertEqual(meeting, nr['calendar.event'])

        self.assertEqual(len(nr.records_map), 2)

        self.assertEqual(nr.main_model, 'res.partner')
