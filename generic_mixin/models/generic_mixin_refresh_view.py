import logging
import threading
import functools
import collections

from odoo import models, api, tools

_logger = logging.getLogger(__name__)


def with_delay_refresh(fn):
    """ Decorator, that automatically wraps method with RefreshViewContext
        context manager

        For example:

            @with_delay_refresh
            def action_do_some_long_running_action(self):
                pass
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        with RefreshViewContext(self.env):
            return fn(self, *args, **kwargs)

    return wrapped


class RefreshViewContext:
    """ Simple context manager, that could be used to send all refresh
        notification with single message. This could be used for optimization
        purposes. Also, it could help, to avoid multiple notification sent to
        browser during long-running transaction.

        :param api.Environment env: the environment to use to send
             notifications
    """
    def __init__(self, env):
        self.env = env
        self.nested = None

    def __enter__(self):
        if hasattr(threading.current_thread(), 'gmrv_refresh_cache'):
            # It seems that this block is executed inside another one.
            # Save the flag on self
            self.nested = True
        else:
            # We have to create thread-level cache, to store all refresh calls
            # Format of cache is:
            # cache = {
            #     'model': {
            #         'action': set(refresh_ids),
            #     },
            # }
            setattr(
                threading.current_thread(),
                'gmrv_refresh_cache',
                collections.defaultdict(
                    functools.partial(
                        collections.defaultdict, set)
                ),
            )

            # We just have created the cache, thus this is top-level block,
            # that needs refresh and cleanup on exit
            self.nested = False

        return self

    def __exit__(self, etype, value, tracback):
        if self.nested:
            # We do not need to do anything if it is not top-level block.
            return False

        gmrv_cache = getattr(threading.current_thread(), 'gmrv_refresh_cache')
        if not etype and gmrv_cache:
            # We have to send notifications only when top-level context
            # manager closed, and there were no errors raised during execution
            # of 'with' body
            self.env['generic.mixin.refresh.view']._gmrv_refresh_view__notify(
                gmrv_cache)

        # Finally cleanup cache, thus notifications will go standard way
        delattr(threading.current_thread(), 'gmrv_refresh_cache')

        # Do not suppress exceptions. If any exception was raised during
        # execution of with bloc, then it will be reraised as is
        return False


class GenericMixinRefreshView(models.AbstractModel):
    """ This mixin could be used to send notifucation to view to refresh
        its content.

        By default, inheriting this mixin will cause automatic refresh of view
        on write. This bechavior could be disabled by setting class (model)
        attribute '_auto_refresh_view_on_write' to False
    """
    _name = 'generic.mixin.refresh.view'
    _description = 'Generic Mixin: Refresh view'

    _auto_refresh_view_on_write = True

    @api.model
    def _auto_refresh_view_on_field_changes(self):
        """ Method have to be overloaded in inherited models
            providing set of fields, changes on specified fields will trigger
            refresh of views on model
        """
        return set()

    @api.model
    @tools.ormcache()
    def _auto_refresh_view_on_field_changes_system(self):
        """ This is system method that have to return default list of fields
            to listen for changes in.
            This method have not be overridden in inherited models
        """
        track_fields = self._auto_refresh_view_on_field_changes()
        if not track_fields:
            # In generator expression the multiple if statements joined as AND
            track_fields = set((
                fname for fname, f in self._fields.items()
                if fname not in ('create_uid', 'write_uid',
                                 'create_date', 'write_date',
                                 self.CONCURRENCY_CHECK_FIELD)
                if not f.compute
                if not f.inverse
                if not f.related
            ))
        return track_fields

    def _gmrv_refresh_view__notify(self, refresh_data):
        """ Notify web client about refreshed records

            :param dict refresh_data: refresh data to be sent ot web client

            Format of refresh_data is following:
            {
                model: {
                    action: set(ids),
                }
            }
        """
        self.env['bus.bus']._sendone(
            'generic_mixin_refresh_view',
            'generic_mixin_refresh_view',
            refresh_data,
        )

    @api.model
    def trigger_refresh_view_for(self, records=None, record_ids=None,
                                 action='write'):
        """ Trigger refresh of views for arbitrary recordset.
            This method will send to webclient suggestion to reload view
            that contains this records

            :param RecordSet records: recordset with records that were updated
            :param list[int] record_ids: list of IDs of records that were
                updated.
            :param str action: action with which records were updated
        """
        res_ids = set()
        if records:
            res_ids |= set(records.ids)
        if record_ids:
            res_ids |= set(record_ids)

        if not res_ids:
            return False

        thread_cache = getattr(
            threading.current_thread(),
            'gmrv_refresh_cache',
            None)
        if thread_cache is not None:
            # If there is defined thread-level cache, then we have to add
            # changes there, instead of sending to bus.bus directly.
            thread_cache[self._name][action] |= res_ids
        else:
            # If there is no cache defined on thread-level, then we send
            # notification to bus.bus directly.
            self._gmrv_refresh_view__notify(
                {
                    self._name: {
                        action: list(res_ids),
                    }
                },
            )
        return True

    def trigger_refresh_view(self, action='write'):
        """ The shortcut method to refresh views that display current recordset
        """
        return self.trigger_refresh_view_for(self, action=action)

    def write(self, vals):
        res = super(GenericMixinRefreshView, self).write(vals)

        if not self._auto_refresh_view_on_write:
            return res

        refresh_fields = self._auto_refresh_view_on_field_changes_system()
        if refresh_fields & set(vals):
            self.trigger_refresh_view(action='write')
        return res

    @api.model_create_multi
    def create(self, vals):
        records = super(GenericMixinRefreshView, self).create(vals)

        if not self._auto_refresh_view_on_write:
            return records

        records.trigger_refresh_view(action='create')

        return records

    def unlink(self):
        record_ids = self.ids
        res = super(GenericMixinRefreshView, self).unlink()

        if not self._auto_refresh_view_on_write:
            return res

        self.trigger_refresh_view_for(record_ids=record_ids, action='unlink')

        return res

    def with_delay_refresh(self):
        """ Use this as context manager, to send refresh notifications issued
            during execution of with block as single message.

            :return RefreshViewContext: context manager

            Example of usage:

                with self.with_delay_refresh():
                    # do some operations that issue multiple refresh messages
        """
        return RefreshViewContext(self.env)
