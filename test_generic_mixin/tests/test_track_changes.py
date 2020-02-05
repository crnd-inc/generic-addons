from odoo.tests.common import SavepointCase


class TrackChangesTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TrackChangesTest, cls).setUpClass()

    def test_track_changes(self):
        # pylint: disable=too-many-statements
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 0)
        self.assertEqual(rec.value2, 0)
        self.assertEqual(rec.value3, 0)
        self.assertEqual(rec.value4, 0)
        self.assertFalse(rec.description)

        rec.value2 = 2

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 0)
        self.assertEqual(rec.value2, 2)
        self.assertEqual(rec.value3, 0)
        self.assertEqual(rec.value4, 0)
        self.assertEqual(rec.description, "v2: 0 -> 2\n")

        rec.value1 = 3

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 3)
        self.assertEqual(rec.value2, 2)
        self.assertEqual(rec.value3, 0)
        self.assertEqual(rec.value4, 0)
        self.assertEqual(rec.description, "v1: 0 -> 3\n")

        rec.write({
            'value1': 5,
            'value2': 7,
        })

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 5)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 0)
        self.assertEqual(rec.value4, 0)
        self.assertEqual(rec.description, "v1: 3 -> 5\nv2: 2 -> 7\n")

        rec.value3 = 2

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 5)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 2)
        self.assertEqual(rec.value4, 0)
        self.assertEqual(rec.description, "v3: 0 -> 2\n")

        rec.value4 = 3

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 5)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 2)
        self.assertEqual(rec.value4, 3)
        self.assertEqual(rec.description, "v4: 0 -> 3\n")

        rec.write({
            'value4': 5,
            'value3': 7,
        })

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 5)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 7)
        self.assertEqual(rec.value4, 5)
        self.assertEqual(rec.description, "v3: 2 -> 7\nv4: 3 -> 5\n")

        rec.write({
            'value1': 9,
            'value4': 8,
            'value3': 6,
        })

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 9)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 6)
        self.assertEqual(rec.value4, 8)
        self.assertEqual(rec.description, "v3: 7 -> 6\nv4: 5 -> 8\n")

        rec.write({
            'value1': 3,
            'value4': 8,  # not changed
            'value3': 6,  # not changed
        })

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 3)
        self.assertEqual(rec.value2, 7)
        self.assertEqual(rec.value3, 6)
        self.assertEqual(rec.value4, 8)
        self.assertEqual(rec.description, "v1: 9 -> 3\n")
