import logging
from contextlib import contextmanager
from odoo import models, api

_logger = logging.getLogger(__name__)


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

    def _lock_for_update(self):
        """ Lock selected records for update.
        """
        if self:
            # pylint: disable=sql-injection
            self.env.cr.execute("""
                SELECT id
                FROM "{table_name}"
                WHERE id IN %(ids)s
                FOR UPDATE NOWAIT;
            """.format(table_name=self._table), {  # nosec
                'ids': tuple(self.ids),
            })

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

        with api.Environment.manage():
            with self.env.registry.cursor() as new_cr:
                new_env = api.Environment(
                    new_cr,
                    self.env.uid,
                    self.env.context.copy())
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
