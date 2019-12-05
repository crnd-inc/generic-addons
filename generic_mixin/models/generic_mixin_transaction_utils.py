import logging
from contextlib import contextmanager
from odoo import registry, models, api

_logger = logging.getLogger(__name__)


class GenericMixinTransactionUtils(models.AbstractModel):
    """ Simple mixin that contains utility methods related to
        transaction management in Odoo.
    """
    _name = 'generic.mixin.transaction.utils'
    _description = 'GenericMixin: Transaction Utils'

    def _lock_for_update(self):
        """ Lock selected records for update
        """
        if self:
            self.env.cr.execute("""
                SELECT id
                FROM "{table_name}"
                WHERE id IN %(ids)s
                FOR UPDATE NOWAIT;
            """.format(table_name=self._table), {
                'ids': tuple(self.ids),
            })

    @contextmanager
    def _in_new_transaction(self):
        """ Start new transaction for selected records

            Example of usage:

                with self._in_new_transaction() as nself:
                    nself.do_some_work()

            If there were no errors caught during do_some_work,
            then changes will be automatically commited.
        """

        with api.Environment.manage():
            with registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(
                    new_cr,
                    self.env.uid,
                    self.env.context.copy())

                yield self.with_env(new_env)
