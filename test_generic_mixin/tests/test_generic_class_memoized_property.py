from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tools.generic_class_memoized_property import (
    GenericClassMemoizedProperty,
)


class TestGenericClassMemoizedProperty(TransactionCase):
    """ Contract tests for the ``GenericClassMemoizedProperty`` descriptor.

        These use plain Python classes (no ORM) to exercise the descriptor
        directly; ``TransactionCase`` is used only so Odoo's runner discovers
        them.
    """

    def test_memoized_once_per_class(self):
        calls = []

        class A:
            @GenericClassMemoizedProperty
            def value(self):
                calls.append(1)
                return {'v': 1}

        a = A()
        self.assertEqual(a.value, {'v': 1})
        self.assertEqual(a.value, {'v': 1})
        # Computed exactly once...
        self.assertEqual(len(calls), 1)
        # ...and shared across instances of the same class (keyed by class).
        self.assertIs(a.value, A().value)

    def test_class_level_access_returns_descriptor_without_computing(self):
        """ Accessing on the class must return the descriptor and must NOT
            compute. This is what makes it immune to abstract-base poisoning
            and safe under ``inspect.getmembers`` scans.
        """
        calls = []

        class A:
            @GenericClassMemoizedProperty
            def value(self):
                calls.append(1)
                return 1

        self.assertIsInstance(A.value, GenericClassMemoizedProperty)
        self.assertEqual(calls, [])

    def test_per_class_isolation(self):
        class Base:
            @GenericClassMemoizedProperty
            def value(self):
                return type(self).__name__

        class A(Base):
            pass

        class B(Base):
            pass

        # Each concrete class computes and caches its own value.
        self.assertEqual(A().value, 'A')
        self.assertEqual(B().value, 'B')

    def test_subclass_not_poisoned_by_base(self):
        """ Regression for the failure mode that killed the class-attribute /
            lazy_classproperty approaches: the base computes an *empty* value
            first, which must NOT shadow a subclass's own (non-empty) value.
        """
        class Base:
            @GenericClassMemoizedProperty
            def handlers(self):
                return sorted(
                    name for name in dir(type(self))
                    if name.startswith('handler_'))

        class Impl(Base):
            def handler_a(self):
                pass

        # Compute the base (empty) FIRST, mimicking abstract-base setup order.
        self.assertEqual(Base().handlers, [])
        # The subclass still gets its own value.
        self.assertEqual(Impl().handlers, ['handler_a'])

    def test_falsy_value_is_cached(self):
        """ An empty/falsy computed value must be a cache hit, not recomputed
            (the descriptor keys on ``KeyError``, not ``is None``).
        """
        calls = []

        class A:
            @GenericClassMemoizedProperty
            def value(self):
                calls.append(1)
                return {}

        a = A()
        self.assertEqual(a.value, {})
        self.assertEqual(a.value, {})
        self.assertEqual(len(calls), 1)

    def test_invalidate_forces_recompute(self):
        calls = []

        class A:
            @GenericClassMemoizedProperty
            def value(self):
                calls.append(1)
                return object()

        a = A()
        v1 = a.value
        self.assertEqual(len(calls), 1)

        # ``A.value`` is the descriptor (class-level access).
        A.value.invalidate(A)

        v2 = a.value
        self.assertEqual(len(calls), 2)
        self.assertIsNot(v1, v2)

    def test_invalidate_unknown_class_is_noop(self):
        class A:
            @GenericClassMemoizedProperty
            def value(self):
                return 1

        # Invalidating a class that was never cached must not raise.
        A.value.invalidate(A)
        self.assertEqual(A().value, 1)

    def test_invalidate_is_per_descriptor(self):
        """ Invalidating one property must not touch a sibling property's
            cache -- so mixins that each own a GenericClassMemoizedProperty
            can invalidate only their own.
        """
        class A:
            @GenericClassMemoizedProperty
            def x(self):
                return object()

            @GenericClassMemoizedProperty
            def y(self):
                return object()

        a = A()
        vx, vy = a.x, a.y
        self.assertIn(A, type(a).x._cache)
        self.assertIn(A, type(a).y._cache)

        type(a).x.invalidate(A)

        # Only ``x`` was dropped.
        self.assertNotIn(A, type(a).x._cache)
        self.assertIn(A, type(a).y._cache)
        self.assertIsNot(a.x, vx)   # recomputed
        self.assertIs(a.y, vy)      # untouched


class TestGenericClassMemoizedPropertyOnModel(TransactionCase):
    """ Integration checks against the real tracking mixin, which uses
        ``GenericClassMemoizedProperty`` for the tracking-handler data.
    """

    def test_tracking_data_is_memoized_and_invalidatable(self):
        model = self.env['test.generic.mixin.track.changes.model']
        cls = type(model)

        data1 = model._generic_tracking_handler_data
        # Same object on repeated access -> memoized.
        self.assertIs(model._generic_tracking_handler_data, data1)
        self.assertTrue(data1['pre_create_handlers'])

        # Class-level access exposes the descriptor; invalidate through it.
        self.assertIsInstance(
            cls._generic_tracking_handler_data,
            GenericClassMemoizedProperty)
        cls._generic_tracking_handler_data.invalidate(cls)

        data2 = model._generic_tracking_handler_data
        # Recomputed (fresh object) but equivalent content.
        self.assertIsNot(data1, data2)
        self.assertEqual(data1['track_fields'], data2['track_fields'])
        self.assertEqual(
            [h['method'] for h in data1['pre_create_handlers']],
            [h['method'] for h in data2['pre_create_handlers']])

    def test_setup_complete_invalidates_tracking_cache(self):
        """ ``_setup_complete`` must drop the memoized handler data, so it is
            recomputed against the fully-assembled class. This is what keeps
            the cache correct across incremental module loading (a later
            module adding handlers) and test ``reset_changes``.
        """
        model = self.env['test.generic.mixin.track.changes.model']
        cls = type(model)
        descriptor = cls._generic_tracking_handler_data

        # Populate the cache.
        self.assertTrue(model._generic_tracking_handler_data)
        self.assertIn(cls, descriptor._cache)

        # A re-setup must invalidate it.
        model._setup_complete()
        self.assertNotIn(cls, descriptor._cache)

        # ...and it recomputes correctly on next access.
        self.assertTrue(
            model._generic_tracking_handler_data['pre_create_handlers'])
