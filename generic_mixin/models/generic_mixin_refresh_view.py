import logging
from odoo import models, api, tools

_logger = logging.getLogger(__name__)


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

        self.env['bus.bus'].sendone(
            'generic_mixin_refresh_view',
            {
                'model': self._name,
                'res_ids': list(res_ids),
                'action': action,
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
