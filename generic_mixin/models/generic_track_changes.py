import logging
import datetime
import collections
from operator import itemgetter
from inspect import getmembers
from odoo import models, api, fields
from odoo.fields import resolve_mro, DATETIME_LENGTH

_logger = logging.getLogger(__name__)

DEFAULT_TRACKING_HANDLER_PRIORITY = 10

FieldChange = collections.namedtuple('FieldChange', ['old_val', 'new_val'])


def pre_write(*track_fields, priority=None):
    """ Declare pre_write hook that will be called on any of specified fields
        changed.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are namedtuples of two elements
        (old_val, new_val), so you can access new or old value as attributes,
        like ``changes['myfield'].new_val``

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
    """ Declare post_write hook that will be called on any of specified fields
        changed.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are namedtuples of two elements
        (old_val, new_val), so you can access new or old value as attributes,
        like ``changes['myfield'].new_val``

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


def pre_create(*track_fields, priority=None):
    """ Declare pre_create hook that will be called before creation of record.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are namedtuples of two elements
        (old_val, new_val), so you can access new or old value as attributes,
        like ``changes['myfield'].new_val``

        If return value is dict, then this values will be used to update
        the data provided to 'create' method of object.

        Note, that these hanndlers will be called on each record in recordset

        for example:

            @pre_create()
            def _pre_create_do_smthng(self, changes):
                fold, fnew = changes.get('field1', [False, False])
                if fnew == 'my value':
                    # do something.

        In case of @pre_create method, the self will be empty.
        So, the method, have to handle this case.
        Especially if you want to decorate method with both:
        @pre_create and @pre_write decorators.

        If track fields specified, then, this method will be called only when
        one of that fields changed.
        If track fields not specified, method will be called in all cases.
    """
    if priority is not None and not isinstance(priority, int):
        raise AssertionError("priority must be int")

    def decorator(func):
        func._pre_create_fields = track_fields
        func._pre_create_priority = priority
        return func
    return decorator


def post_create(*track_fields, priority=None):
    """ Declare post_create hook that will be called after record was created.

        The decorated method must receive 'changes' param, that is dict, where
        keys are names of fields, and values are namedtuples of two elements
        (old_val, new_val), so you can access new or old value as attributes,
        like ``changes['myfield'].new_val``

        Return value is ignored.

        Note, that these hanndlers will be called on each record in recordset

        For example:

            @post_create()
            def _post_create_do_smthng(self, changes):
                fold, fnew = changes.get('field1', [False, False])
                if fnew == 'my value':
                    # do something.

        Or we can specify the list of fields that have to be present in vals,
        to call this method. For example:

            @post_create('field1')
            def _post_create_do_smthng(self, changes):
                if changes['field1'].new_val == 'my value':
                    # do something.

        In case of @post_create method, self will be single just created record

        If track fields specified, then, this method will be called only when
        one of that fields changed.
        If track fields not specified, method will be called in all cases.
    """
    if priority is not None and not isinstance(priority, int):
        raise AssertionError("priority must be int")

    def decorator(func):
        func._post_create_fields = track_fields
        func._post_create_priority = priority
        return func
    return decorator


def is_tracking_handler(func):
    """ Check if method (func) is tracking handler
    """
    if not callable(func):
        return False
    if hasattr(func, '_pre_write_fields'):
        return True
    if hasattr(func, '_post_write_fields'):
        return True
    if hasattr(func, '_pre_create_priority'):
        return True
    if hasattr(func, '_post_create_priority'):
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


def check_method_has_attr_via_mro(obj, method_name, attr_name):
    """ Check that method has specified attr in MRO
    """
    for method in resolve_mro(obj, method_name, callable):
        if hasattr(method, attr_name):
            return True
    return False


class FieldChangeHandler:
    """ Representation of field change handler method.

        This class is used only during model-creation process,
        to simplify code responsible for analysing methods
    """
    def __init__(self, obj, method_name):
        self._obj = obj
        self._method_name = method_name

        # Parse fields info
        self.pre_write_fields = self._get_tracking_fields('_pre_write_fields')
        self.post_write_fields = self._get_tracking_fields(
            '_post_write_fields')
        self.pre_create_fields = self._get_tracking_fields(
            '_pre_create_fields')
        self.post_create_fields = self._get_tracking_fields(
            '_post_create_fields')

        # Pars flags pre/post create
        self.is_pre_create = check_method_has_attr_via_mro(
            self._obj, self._method_name, '_pre_create_priority')
        self.is_post_create = check_method_has_attr_via_mro(
            self._obj, self._method_name, '_post_create_priority')

    def _get_tracking_fields(self, fields_attr):
        return get_method_fields_via_mro(
            self._obj, self._method_name, fields_attr)

    @property
    def name(self):
        """ Return method name
        """
        return self._method_name

    def get_priority(self, priority_attr):
        """ Could be called to get priority from method attr
        """
        return get_method_priority_via_mro(
            self._obj, self._method_name, priority_attr,
            DEFAULT_TRACKING_HANDLER_PRIORITY)

    def validate(self):
        """ Validate the handler.
            At this moment just prints warnings to the log.
        """
        if self.pre_write_fields and self.post_write_fields:
            _logger.warning(
                "Method must not be decorated as @pre_write and "
                "@post_write at same time! Method: %s", self._method_name)

        if self.is_pre_create and self.is_post_create:
            _logger.warning(
                "Method must not be decorated as @pre_create and "
                "@post_create at same time! Method: %s", self._method_name)

        # Validate pre_write_fields
        for name in self.pre_write_fields:
            if name not in self._obj._fields:
                _logger.warning(
                    "@pre_write%r (%s) parameters must be "
                    "field name (%s)",
                    tuple(self.pre_write_fields), self._method_name, name)

        # Validate post_write_fields
        for name in self.post_write_fields:
            if name not in self._obj._fields:
                _logger.warning(
                    "@post_write%r (%s) parameters must be "
                    "field name (%s)",
                    tuple(self.post_write_fields), self._method_name, name)

        # Validate pre_create_fields
        for name in self.pre_create_fields:
            if name not in self._obj._fields:
                _logger.warning(
                    "@pre_create%r (%s) parameters must be "
                    "field name (%s)",
                    tuple(self.pre_write_fields), self._method_name, name)

        # Validate post_create_fields
        for name in self.post_create_fields:
            if name not in self._obj._fields:
                _logger.warning(
                    "@post_create%r (%s) parameters must be "
                    "field name (%s)",
                    tuple(self.post_write_fields), self._method_name, name)


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

        Pre and Post Write decorators
        -----------------------------

        To simplify code handling changes of fields, you can use
        @pre_write and @post_write decorators, to decorate methods that
        have to be called on field changes

        Pre and Post Create decorators
        ------------------------------

        To simplify code handling creation of records in similar way
        as @pre_write and @post_write methods do, you can use
        @pre_create and @post_create decorators. One of the benefits of this
        approach, is that you can decorate single method with both
        @pre_create and @pre_write or @post_create and @post_write decorators.
        This could be used for cases, when you need to run some code
        before create and before write (for example preprocess vals).
        Or, you can use pair of @post_create and @post_write decorators,
        to run some operation after record creation and after
        some changes to record.

        For example:

            @post_create()
            @post_write('state', 'date')
            def run_some_post_processing(self, changes):
                # do something, recompute some field, etc

    """
    _name = 'generic.mixin.track.changes'
    _description = 'Generic Mixin: Track Changes'

    @api.model
    def _get_generic_tracking_fields(self):
        """ Compute set of filed to track changes.

            :rtype: set
            :return: set of fields track changes of
        """
        return self._generic_tracking_handler_data['track_fields']

    @property
    def _generic_tracking_handler_data(self):
        """ Return a dictionary mapping field names to post write handlers. """
        # collect tracking fields on the model's class
        cls = type(self)
        write_handlers = {}
        pre_write_handlers = write_handlers['pre_write_handlers'] = []
        post_write_handlers = write_handlers['post_write_handlers'] = []
        pre_create_handlers = write_handlers['pre_create_handlers'] = []
        post_create_handlers = write_handlers['post_create_handlers'] = []
        track_fields = write_handlers['track_fields'] = set()

        for method_name, __ in getmembers(cls, is_tracking_handler):
            handler = FieldChangeHandler(self, method_name)
            handler.validate()

            if handler.pre_write_fields:
                pre_write_handlers += [{
                    'method': handler.name,
                    'priority': handler.get_priority('_pre_write_priority'),
                    'fields': tuple(handler.pre_write_fields),
                }]

            if handler.post_write_fields:
                post_write_handlers += [{
                    'method': handler.name,
                    'priority': handler.get_priority('_post_write_priority'),
                    'fields': tuple(handler.post_write_fields),
                }]

            if handler.is_pre_create:
                pre_create_handlers += [{
                    'method': handler.name,
                    'priority': handler.get_priority('_pre_create_priority'),
                    'fields': tuple(handler.pre_create_fields),
                }]
            if handler.is_post_create:
                post_create_handlers += [{
                    'method': handler.name,
                    'priority': handler.get_priority('_post_create_priority'),
                    'fields': tuple(handler.post_create_fields),
                }]

            track_fields |= handler.pre_write_fields
            track_fields |= handler.post_write_fields

        # Sort handlers
        pre_write_handlers.sort(key=itemgetter('priority'))
        post_write_handlers.sort(key=itemgetter('priority'))
        pre_create_handlers.sort(key=itemgetter('priority'))
        post_create_handlers.sort(key=itemgetter('priority'))

        # optimization: memoize result on cls, it will not be recomputed
        cls._generic_tracking_handler_data = write_handlers
        return write_handlers

    @classmethod
    def _init_constraints_onchanges(cls):
        # reset properties memoized on cls
        cls._generic_tracking_handler_data = (
            GenericMixInTrackChanges._generic_tracking_handler_data)
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
                        changes[record.id][field] = FieldChange(old_value,
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
        for hdl in self._generic_tracking_handler_data['pre_write_handlers']:
            if set(hdl['fields']) & set(changes):
                handler_res = getattr(self, hdl['method'])(changes)
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
        self.ensure_one()
        for hdl in self._generic_tracking_handler_data['post_write_handlers']:
            if set(hdl['fields']) & set(changes):
                getattr(self, hdl['method'])(changes)

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

    def _create__get_changed_fields(self, vals):
        """ Prepare dict with changes, computed from 'create' method

            Similar to 'get_changed_fields', but use empty record to
            compute old_val.
        """
        # Prepare dict with changes
        # changes = {
        #     field1: (old_value, new_value),
        # }

        # Generate changes, using empty record as old value
        # TODO: may be it have sense to handle default values here
        changes = {}
        dummy_record = self.browse()
        for fname, fval in vals.items():
            old_value = dummy_record[fname]
            field = self._fields[fname]

            # Workaround to handle incorrect datetime values in 'mail' module's
            # demo data. For example, if value for datetime field looks like:
            # '2021-10-20 11:04' (without seconds block)
            if (fval and field.type == 'datetime' and
                    isinstance(fval, str) and
                    len(fval) <= DATETIME_LENGTH):
                try:
                    # At first try to do it in standard way
                    fval = fields.Datetime.to_datetime(fval)
                except ValueError:
                    # And if not working, apply special case
                    fval = datetime.datetime.strptime(fval, '%Y-%m-%d %H:%M')

            new_value = self._fields[fname].convert_to_record(
                self._fields[fname].convert_to_cache(fval, self),
                self)
            if old_value != new_value:
                changes[fname] = FieldChange(old_value, new_value)
        return changes

    @api.model
    def create(self, vals):
        changes = self._create__get_changed_fields(vals)

        # Run pre-create hooks and update vals with new changes (if needed)
        vals = dict(vals)
        for hdl in self._generic_tracking_handler_data['pre_create_handlers']:
            if not hdl['fields'] or set(hdl['fields']) & set(changes):
                handler_res = getattr(self, hdl['method'])(changes)
                if handler_res and isinstance(handler_res, dict):
                    vals.update(handler_res)

        record = super(GenericMixInTrackChanges, self).create(vals)

        # Run post-create handlers
        for hdl in self._generic_tracking_handler_data['post_create_handlers']:
            if not hdl['fields'] or set(hdl['fields']) & set(changes):
                getattr(record, hdl['method'])(changes)

        return record
