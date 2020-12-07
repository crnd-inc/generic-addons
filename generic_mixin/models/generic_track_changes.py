import logging
import collections
from operator import itemgetter
from inspect import getmembers
from odoo import models, api
from odoo.fields import resolve_mro

_logger = logging.getLogger(__name__)

DEFAULT_WRITE_HANDER_PRIORITY = 10


def pre_write(*track_fields, priority=None):
    """ Declare pre_write hook that will be called on any of specified fields
        changed.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are tuples of two elements
        (old_value, new_value).

        If return value is dict, then this values will be used to update
        record before calling post processing.

        Note, that these hanndlers will be called on each record in recordset

        for example:

            @pre_write('field1', 'field2')
            def _pre_fields12_changed(self, changes):
                fold, fnew = changes.get('field1', [False, False])
                if fnew == 'my value':
                    # do something.
    """
    if priority is not None and not isinstance(priority, int):
        raise AssertionError("priority must be int")

    def decorator(func):
        func._pre_write_fields = track_fields
        func._pre_write_priority = priority
        return func
    return decorator


def post_write(*track_fields, priority=None):
    """ Declare pre_write hook that will be called on any of specified fields
        changed.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are tuples of two elements
        (old_value, new_value).

        Return value is ignored.

        Note, that these hanndlers will be called on each record in recordset

        For example:

            @post_write('field1', 'field2')
            def _post_fields12_changed(self, changes):
                fold, fnew = changes.get('field1', [False, False])
                if fnew == 'my value':
                    # do something.
    """
    if priority is not None and not isinstance(priority, int):
        raise AssertionError("priority must be int")

    def decorator(func):
        func._post_write_fields = track_fields
        func._post_write_priority = priority
        return func
    return decorator


def is_write_handler(func):
    """ Check if method (func) is write handler
    """
    if not callable(func):
        return False
    if hasattr(func, '_pre_write_fields'):
        return True
    if hasattr(func, '_post_write_fields'):
        return True
    return False


def get_method_fields_via_mro(obj, method_name, attr_name):
    """ Get set of all fields metioned in attr 'attr_name' of method in all
        method overrides in subclasses
    """
    return set(
        field
        for method in resolve_mro(obj, method_name, callable)
        for field in getattr(method, attr_name, [])
    )


def get_method_priority_via_mro(obj, method_name, attr_name, default):
    """ Get the priority for method from attr 'attr_name',
        checking all overrides in mro order and looking for first non None
        value. If no such value found, then default value will be applied
    """
    for method in resolve_mro(obj, method_name, callable):
        meth_val = getattr(method, attr_name, None)
        if meth_val is not None:
            return meth_val
    return default


class GenericMixInTrackChanges(models.AbstractModel):
    """ Simple mixin to provide mechanism to track changes of objects

        How to use
        ----------

        1. Inerit your model from 'generic.mixin.track.changes'
        2. Override '_get_generic_tracking_fields' method to return
           set of fields to track changes of.
        3. Override '_preprocess_write_changes' to add preprocessing
        4. Override '_postprocess_write_changes' to add postprocessing.
        5. Thats all

        Details
        -------

        Both methods '_postprocess_write_changes' and
        '_preprocess_write_changes' have to be designed to process single
        record. Each method receives 'changes' param that is dictionary, where
        keys are names of fields, and values are tuples of two elements:
        (old_value, new_value).

        Pre and Post write decorators
        -----------------------------

        To simplify code handling changes of fields, you can use
        @pre_write and @post_write decorators, to decorate methods that
        have to be called on field changes
    """
    _name = 'generic.mixin.track.changes'
    _description = 'Generic Mixin: Track Changes'

    @api.model
    def _get_generic_tracking_fields(self):
        """ Compute set of filed to track changes.

            :rtype: set
            :return: set of fields track changes of
        """
        return self._write_handler_data['track_fields']

    @property
    def _write_handler_data(self):
        """ Return a dictionary mapping field names to post write handlers. """
        # collect tracking fields on the model's class
        cls = type(self)
        write_handlers = {}
        pre_write_handlers = write_handlers['pre_write_handlers'] = []
        post_write_handlers = write_handlers['post_write_handlers'] = []
        track_fields = write_handlers['track_fields'] = set()

        for method_name, __ in getmembers(cls, is_write_handler):
            # TODO: do only one iteration over method overrides
            pre_write_fields = get_method_fields_via_mro(
                self, method_name, '_pre_write_fields')
            post_write_fields = get_method_fields_via_mro(
                self, method_name, '_post_write_fields')

            if pre_write_fields and post_write_fields:
                _logger.warning(
                    "Method must not be decorated as @pre_write and "
                    "@post_write at same time! Method: %s", method_name)

            # Validate pre_write_fields
            for name in pre_write_fields:
                if name not in self._fields:
                    _logger.warning(
                        "@pre_write%r (%s) parameters must be "
                        "field name (%s)",
                        tuple(pre_write_fields), method_name, name)

            # Validate post_write_fields
            for name in post_write_fields:
                if name not in self._fields:
                    _logger.warning(
                        "@post_write%r (%s) parameters must be "
                        "field name (%s)",
                        tuple(post_write_fields), method_name, name)

            if pre_write_fields:
                pre_write_handlers += [{
                    'method': method_name,
                    'priority': get_method_priority_via_mro(
                        self, method_name, '_pre_write_priority',
                        DEFAULT_WRITE_HANDER_PRIORITY),
                    'fields': tuple(pre_write_fields),
                }]

            if post_write_fields:
                post_write_handlers += [{
                    'method': method_name,
                    'priority': get_method_priority_via_mro(
                        self, method_name, '_post_write_priority',
                        DEFAULT_WRITE_HANDER_PRIORITY),
                    'fields': tuple(post_write_fields),
                }]

            track_fields |= pre_write_fields
            track_fields |= post_write_fields

        # Sort handlers
        pre_write_handlers.sort(key=itemgetter('priority'))
        post_write_handlers.sort(key=itemgetter('priority'))

        # optimization: memoize result on cls, it will not be recomputed
        cls._write_handler_data = write_handlers
        return write_handlers

    @classmethod
    def _init_constraints_onchanges(cls):
        # reset properties memoized on cls
        cls._write_handler_data = (
            GenericMixInTrackChanges._write_handler_data)
        return super(
            GenericMixInTrackChanges, cls)._init_constraints_onchanges()

    def _get_changed_fields(self, vals):
        """ Preprocess vals to be written, and gether field changes
        """
        field_names = self._get_generic_tracking_fields()
        changes = collections.defaultdict(dict)
        changed_fields = set(field_names) & set(vals.keys())
        if changed_fields:
            # changes = {
            #     record_id: {
            #         field1: (old_value, new_value),
            #     }
            # }
            for record in self:
                for field in changed_fields:
                    old_value = record[field]
                    new_value = self._fields[field].convert_to_record(
                        self._fields[field].convert_to_cache(
                            vals[field], self),
                        self)
                    if old_value != new_value:
                        changes[record.id][field] = (old_value,
                                                     new_value)
        return dict(changes)

    def _preprocess_write_changes(self, changes):
        """ Called before write, and could be used to do some pre-processing.

            Please, do not call `self.write` in overrides of this method.
            If you need to modify values to be sent to 'write',
            then just update returned dictionary with desired values.

            This method may be overridden by other addons to add
            some preprocessing of changes, before write

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :rtype: dict
            :return: values to update record with.
                     These values will be written just after write
        """
        self.ensure_one()
        res = {}
        for handler in self._write_handler_data['pre_write_handlers']:
            if set(handler['fields']) & set(changes):
                handler_res = getattr(self, handler['method'])(changes)
                if handler_res and isinstance(handler_res, dict):
                    res.update(handler_res)
        return res

    def _postprocess_write_changes(self, changes):
        """ Called after write

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """
        for handler in self._write_handler_data['post_write_handlers']:
            if set(handler['fields']) & set(changes):
                getattr(self, handler['method'])(changes)
        self.ensure_one()

    def write(self, vals):
        changes = self._get_changed_fields(vals)

        # Store here updates got from preprocessing
        updates = collections.defaultdict(dict)
        for record in self:
            if record.id in changes:
                updates[record.id] = record._preprocess_write_changes(
                    changes[record.id])

        res = super(GenericMixInTrackChanges, self).write(vals)

        # Update records (using values from pre-processing) and apply post
        # processing
        for record in self:
            if record.id in updates:
                super(GenericMixInTrackChanges, record).write(
                    updates[record.id])
            if record.id in changes:
                record._postprocess_write_changes(changes[record.id])
        return res
