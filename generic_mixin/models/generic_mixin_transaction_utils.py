import functools
import hashlib
import logging
import struct
from contextlib import contextmanager

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _advisory_lock_id(lock_key):
    """Convert an arbitrary string key to a positive int8 for PostgreSQL
    advisory lock functions.  Uses SHA-256 for deterministic, uniform
    distribution across processes and restarts.
    """
    digest = hashlib.sha256(lock_key.encode()).digest()
    return struct.unpack('>q', digest[:8])[0] & 0x7FFFFFFFFFFFFFFF


def advisory_locked(method=None, *, lock_key=None, transaction_level=True):
    """Decorator that wraps an Odoo model method in an advisory lock.

    The lock key defaults to ``"{model._name}.{method.__name__}"``.
    Override with an explicit *lock_key* string when needed.

    :param str lock_key: explicit lock key (default: auto-generated)
    :param bool transaction_level: passed to ``_advisory_lock``

    Usage::

        class MyModel(models.Model):
            _inherit = 'generic.mixin.transaction.utils'

            @advisory_locked
            def do_heavy_work(self):
                ...

            @advisory_locked(lock_key="my_custom_lock")
            def do_other_work(self):
                ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            key = lock_key or f"{self._name}.{func.__name__}"
            with self._advisory_lock(
                key, transaction_level=transaction_level,
            ):
                return func(self, *args, **kwargs)
        return wrapper

    if method is not None:
        # Called as @advisory_locked without parentheses
        return decorator(method)
    # Called as @advisory_locked(...) with arguments
    return decorator


class GenericMixinTransactionUtils(models.AbstractModel):
    """ Simple mixin that contains utility methods related to
        transaction management in Odoo.

        This mixin is useful for long-running operations and helps to
        avoid deadlocks.

        For example, you may write code like following in some scheduler:

            for record in records:
                with record._in_new_transaction() as nrec:
                    nrec._lock_for_update()
                    # do your long-runnning operation and be sure, that if
                    # record was precessed successufully changes will be
                    # commited.
    """
    _name = 'generic.mixin.transaction.utils'
    _description = 'GenericMixin: Transaction Utils'

    @contextmanager
    def _advisory_lock(self, lock_key, no_raise=False,
                       transaction_level=True):
        """Acquire a PostgreSQL advisory lock for the duration of the
        ``with`` block.

        :param str lock_key: arbitrary string used to derive the lock id
        :param bool no_raise: when ``True``, yield ``False`` instead of
            raising if the lock is already held by another session
        :param bool transaction_level: when ``True`` (default), use a
            transaction-level lock (``pg_try_advisory_xact_lock``) that
            is released automatically on commit/rollback — safe with
            connection pooling.  When ``False``, use a session-level
            lock (``pg_try_advisory_lock``) that is explicitly unlocked
            when the ``with`` block exits — use this when work after the
            block should not hold the lock.

        Example::

            with self._advisory_lock("my_operation"):
                # exclusive section — only one session at a time
                self.do_work()

            # With no_raise:
            with self._advisory_lock("my_op", no_raise=True) as acquired:
                if acquired:
                    self.do_work()
        """
        lock_id = _advisory_lock_id(lock_key)
        lock_func = (
            "pg_try_advisory_xact_lock"
            if transaction_level
            else "pg_try_advisory_lock"
        )
        self.env.cr.execute(
            "SELECT %s(%%s)" % lock_func, [lock_id])  # nosec
        acquired = self.env.cr.fetchone()[0]
        if not acquired:
            if no_raise:
                _logger.warning(
                    "Advisory lock %r (id=%s) is already held, skipping",
                    lock_key, lock_id)
                yield False
                return
            raise UserError(self.env._(
                "Another process is already running this operation. "
                "Please try again later."
            ))
        try:
            yield True
        finally:
            if not transaction_level:
                self.env.cr.execute(
                    "SELECT pg_advisory_unlock(%s)", [lock_id])

    def _lock_for_update(self):
        """ Lock selected records for update.
        """
        if self:
            # pylint: disable=sql-injection
            self.env.cr.execute(  # nosec
                """
                    SELECT id
                    FROM "{table_name}"
                    WHERE id IN %(ids)s
                    FOR UPDATE NOWAIT;
                """.format(table_name=self._table), {  # nosec
                    'ids': tuple(self.ids),
                }
            )

    @contextmanager
    def _in_new_transaction(self, lock=False, no_raise=False):
        """ Start new transaction for selected records

            :param bool lock: lock records in self for update (nowait)
            :param bool no_raise: Do not raise errors,
                                  just roll back transaction instead

            Example of usage:

                with self._in_new_transaction() as nself:
                    nself.do_some_work()

            If there were no errors caught during do_some_work,
            then changes will be automatically commited.
        """

        with self.env.registry.cursor() as new_cr:
            new_env = self.env(cr=new_cr)
            nself = self.with_env(new_env)

            if lock:
                nself._lock_for_update()

            try:
                yield nself
            except Exception:
                if no_raise:
                    _logger.warning(
                        "Error caught while processing %s in transaction",
                        self, exc_info=True)
                    new_cr.rollback()
                else:
                    raise
            else:
                # We need to flush, to ensure all pending computations are
                # saved into DB before commiting and closing cursor
                new_cr.flush()

    def _iter_in_transact(self, lock=False, no_raise=False):
        """ Iterate over records in self, yield each record wrapped in separate
            transaction

            :param bool lock: lock records in self for update (nowait)
            :param bool no_raise: Do not raise errors,
                                  just roll back transaction instead

            Example of usage:

                for rec in self._iter_in_transact():
                    rec.do_some_operation()

        """
        for rec in self:
            with rec._in_new_transaction(lock=lock, no_raise=no_raise) as nrec:
                yield nrec
