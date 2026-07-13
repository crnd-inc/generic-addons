import weakref


class GenericClassMemoizedProperty:
    """ Descriptor that memoizes a value computed once per *model class*.

        The value is kept in a per-descriptor ``WeakKeyDictionary`` keyed by
        the concrete model class -- never on the class itself. Compared to a
        self-overwriting property (``cls._attr = value``) this:

        * never mutates the model class, so it does not trip the test
          framework's guard against model-class mutations during tests;
        * is not shadowed on abstract bases (class access returns the
          descriptor and never computes), so subclasses are not poisoned;
        * is per-registry and recomputes on registry rebuild (a new class
          object is a cache miss); weak keys let dropped registries be freed.

        The cached value must be a pure function of the model *class* (stable
        for a registry's lifetime). It is NOT refreshed for a *reused* class
        whose definition changed (e.g. incremental module load, a patched
        method); invalidate it in the model's setup hook (see ``invalidate``).
        ``fget`` must not read its own cached attribute (infinite recursion)
        and should be idempotent (concurrent access may compute twice).

        Usage::

            class MyModel(models.AbstractModel):

                @GenericClassMemoizedProperty
                def _my_state(self):
                    return ...  # computed from ``type(self)``

                def _setup_complete(self):  # _post_model_setup__ on 19.0
                    res = super()._setup_complete()
                    type(self)._my_state.invalidate(type(self))
                    return res
    """
    def __init__(self, fget):
        self.fget = fget
        self.name = getattr(fget, '__name__', None)
        self.__doc__ = fget.__doc__
        self._cache = weakref.WeakKeyDictionary()

    def __set_name__(self, owner, name):
        self.name = name

    def __repr__(self):
        return '<GenericClassMemoizedProperty %s>' % (self.name,)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        cls = type(instance)
        try:
            # KeyError, not ``.get() is None``, so a falsy value (e.g. {})
            # is still a cache hit.
            return self._cache[cls]
        except KeyError:
            value = self._cache[cls] = self.fget(instance)
            return value

    def invalidate(self, cls):
        """ Drop the memoized value for ``cls`` (if any).

            Call it from the owning mixin's setup hook as
            ``type(self)._attr.invalidate(type(self))`` to refresh the value on
            every re-setup: the class object is reused across ``setup_models``,
            so an earlier value could otherwise stay stale. Off-class, so it
            never trips the model-mutation guard.
        """
        self._cache.pop(cls, None)
