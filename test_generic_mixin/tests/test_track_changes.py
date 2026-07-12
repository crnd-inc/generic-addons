from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.models.generic_track_changes import (
    GenericMixInTrackChanges,
)


class TrackChangesTest(TransactionCase):

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
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')
        self.assertEqual(rec.create_dbg3, 'pre-create-3')
        self.assertEqual(rec.create_dbg4, 'post-create-4')

        rec.value2 = 2

        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value1, 0)
        self.assertEqual(rec.value2, 2)
        self.assertEqual(rec.value3, 0)
        self.assertEqual(rec.value4, 0)
        self.assertEqual(rec.description, "v2: 0 -> 2\n")
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')
        self.assertEqual(rec.create_dbg3, 'pre-create-3')
        self.assertEqual(rec.create_dbg4, 'post-create-4')

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

    def test_track_changes_2(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value5, 0)
        self.assertEqual(rec.value11, 0)
        self.assertEqual(rec.value21, 0)
        self.assertFalse(rec.description)
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')
        self.assertEqual(rec.create_dbg3, 'pre-create-3')
        self.assertEqual(rec.create_dbg4, 'post-create-4')

        rec.value5 = 53

        self.assertEqual(rec.description, "Test V5 change Overriden")
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')

    def test_track_changes_3(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value5, 0)
        self.assertEqual(rec.value11, 0)
        self.assertEqual(rec.value21, 0)
        self.assertFalse(rec.description)
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')
        self.assertEqual(rec.create_dbg3, 'pre-create-3')
        self.assertEqual(rec.create_dbg4, 'post-create-4')

        rec.value21 = 243

        self.assertEqual(rec.description, "Test V5 change Overriden")
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')

        rec.write({
            'create_dbg': 'test',
            'description': 'test',
            'create_dbg2': 'test',
        })
        self.assertEqual(rec.description, "test")
        self.assertEqual(rec.create_dbg, 'test')
        self.assertEqual(rec.create_dbg2, 'test')

        rec.value21 = 74

        self.assertEqual(rec.description, "Test V5 change Overriden")
        self.assertEqual(rec.create_dbg, 'test')
        self.assertEqual(rec.create_dbg2, 'post-create-1')

    def test_track_changes_4(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertEqual(rec.name, 'Test')
        self.assertEqual(rec.value5, 0)
        self.assertEqual(rec.value11, 0)
        self.assertEqual(rec.value21, 0)
        self.assertFalse(rec.description)
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')
        self.assertEqual(rec.create_dbg3, 'pre-create-3')
        self.assertEqual(rec.create_dbg4, 'post-create-4')

        rec.value11 = 28

        self.assertEqual(rec.description, "Test V5 change Overriden")
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')

        rec.write({
            'create_dbg': 'test',
            'description': 'test',
            'create_dbg2': 'test',
        })
        self.assertEqual(rec.description, "test")
        self.assertEqual(rec.create_dbg, 'test')
        self.assertEqual(rec.create_dbg2, 'test')

        rec.value11 = 31

        self.assertEqual(rec.description, "Test V5 change Overriden")
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'test')

    def test_track_changes_priority_1(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertFalse(rec.description)

        rec.value6 = 42

        self.assertEqual(rec.description, 'Priority 6-15')

    def test_track_changes_priority_2(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertFalse(rec.description)

        rec.value7 = 13

        self.assertEqual(rec.description, 'Priority 7-15')

    def test_track_changes_priority_3(self):
        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
        })
        self.assertFalse(rec.description)

        rec.value8 = 773

        # None - means priority 10, and have to be executed after priority 5
        self.assertEqual(rec.description, 'Priority 8-None')

    def test_track_changes_datetime(self):

        Model = self.env['test.generic.mixin.track.changes.model']

        rec = Model.create({
            'name': 'Test',
            'dt_value': '2021-11-13 12:13:14',
        })

        self.assertEqual(rec.dt_value, fields.Datetime.to_datetime(
            '2021-11-13 12:13:14'))

        rec = Model.create({
            'name': 'Test',
            'dt_value': '2021-11-13 12:13',
        })

        self.assertEqual(rec.dt_value, fields.Datetime.to_datetime(
            '2021-11-13 12:13:00'))

    def test_handler_data_class_access_does_not_poison(self):
        """ Accessing '_generic_tracking_handler_data' at class level (as
            Odoo's setup-time introspection does) must not memoize a result
            that leaks to concrete models.

            Regression test: a memoization that computes on class access and
            caches on the abstract mixin base would compute an *empty* handler
            set (the bare mixin declares no handlers) and every concrete model
            would inherit it, so no handler would ever fire.
        """
        # Touch class-level access on the abstract mixin and on the concrete
        # model class *before* creating any record.
        self.assertIsNotNone(
            GenericMixInTrackChanges._generic_tracking_handler_data)
        Model = self.env['test.generic.mixin.track.changes.model']
        self.assertIsNotNone(type(Model)._generic_tracking_handler_data)

        # Handlers must still fire for the concrete model.
        rec = Model.create({'name': 'Test'})
        self.assertEqual(rec.create_dbg, 'pre-create-1')
        self.assertEqual(rec.create_dbg2, 'post-create-1')

    def test_handler_data_recomputed_after_invalidate(self):
        """ After the memoized handler data is invalidated, it is recomputed
            and handlers keep working. Regression test for invalidation.
        """
        Model = self.env['test.generic.mixin.track.changes.model']

        # Populate the cache.
        rec = Model.create({'name': 'Test'})
        self.assertEqual(rec.create_dbg, 'pre-create-1')

        # Drop the memoized handler data (as one would when the model's
        # handler set changes on a reused class).
        cls = type(Model)
        cls._generic_tracking_handler_data.invalidate(cls)

        # Handlers must keep working after invalidation + recomputation.
        rec2 = Model.create({'name': 'Test2'})
        self.assertEqual(rec2.create_dbg, 'pre-create-1')
        self.assertEqual(rec2.create_dbg2, 'post-create-1')

    def test_handler_data_isolated_across_models(self):
        """ Two real models that both inherit the tracking mixin but declare
            different handler sets must each resolve to their own data.

            A model that inherits the mixin but declares no handlers must
            resolve to an *empty* handler set -- and, crucially, this must not
            make the model that DOES declare handlers resolve empty (the
            abstract-base poisoning failure mode, checked here on real models).
        """
        with_handlers = self.env['test.generic.mixin.track.changes.model']
        without_handlers = self.env['test.generic.mixin.multi.interface.impl']

        with_data = with_handlers._generic_tracking_handler_data
        without_data = without_handlers._generic_tracking_handler_data

        self.assertTrue(with_data['pre_create_handlers'])
        self.assertEqual(without_data['pre_create_handlers'], [])
        self.assertEqual(without_data['post_write_handlers'], [])
        # Distinct cache entries, not a shared (poisoned) one.
        self.assertIsNot(with_data, without_data)
