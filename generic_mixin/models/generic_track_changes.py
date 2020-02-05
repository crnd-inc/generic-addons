import logging
import collections
from inspect import getmembers
from odoo import models, api

_logger = logging.getLogger(__name__)


def pre_write(*track_fields):
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
    def decorator(func):
        func._pre_write_fields = track_fields
        return func
    return decorator


def post_write(*track_fields):
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
    def wrapper(func):
        func._post_write_fields = track_fields
        return func
    return wrapper


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
        return self._write_handler_tracking_fields

    @property
    def _pre_write_handlers(self):
        def is_pre_write_handler(func):
            return callable(func) and hasattr(func, '_pre_write_fields')

        # collect pre-write methods on the model's class
        cls = type(self)
        methods = []
        for __, func in getmembers(cls, is_pre_write_handler):
            for name in func._pre_write_fields:
                if name not in cls._fields:
                    _logger.warning(
                        "@pre_write%r parameters must be field names (%s)",
                        func._pre_write_fields, name)
            methods.append(func)

        # optimization: memoize result on cls, it will not be recomputed
        cls._pre_write_handlers = methods
        return methods

    @property
    def _post_write_handlers(self):
        def is_post_write_handler(func):
            return callable(func) and hasattr(func, '_post_write_fields')

        # collect post-write methods on the model's class
        cls = type(self)
        methods = []
        for __, func in getmembers(cls, is_post_write_handler):
            for name in func._post_write_fields:
                if name not in cls._fields:
                    _logger.warning(
                        "@post_write%r parameters must be field names (%s)",
                        func._post_write_fields, name)
            methods.append(func)

        # optimization: memoize result on cls, it will not be recomputed
        cls._post_write_handlers = methods
        return methods

    @property
    def _write_handler_tracking_fields(self):
        """ Return a dictionary mapping field names to post write handlers. """
        def is_write_handler(func):
            if not callable(func):
                return False
            if hasattr(func, '_pre_write_fields'):
                return True
            if hasattr(func, '_post_write_fields'):
                return True
            return False

        # collect tracking fields on the model's class
        cls = type(self)
        track_fields = set()
        for __, func in getmembers(cls, is_write_handler):
            track_fields |= set(getattr(func, '_pre_write_fields', []))
            track_fields |= set(getattr(func, '_post_write_fields', []))

        # optimization: memoize result on cls, it will not be recomputed
        cls._write_handler_tracking_fields = track_fields
        return track_fields

    @classmethod
    def _init_constraints_onchanges(cls):
        # reset properties memoized on cls
        cls._pre_write_handlers = GenericMixInTrackChanges._pre_write_handlers
        cls._post_write_handlers = (
            GenericMixInTrackChanges._post_write_handlers)
        cls._write_handler_tracking_fields = (
            GenericMixInTrackChanges._write_handler_tracking_fields)
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
        for handler in self._pre_write_handlers:
            if set(handler._pre_write_fields) & set(changes):
                handler_res = handler(self, changes)
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
        for handler in self._post_write_handlers:
            if set(handler._post_write_fields) & set(changes):
                handler(self, changes)
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
