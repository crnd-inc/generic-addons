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
    def trigger_refresh_view_for(self, records):
        """ Triggre refresh of views for arbitary recordset.
            This method will send to webclient suggestion to reload view
            that contains this records
        """
        if not records:
            return False
        self.env['bus.bus'].sendone(
            'generic_mixin_refresh_view',
            {
                'model': records._name,
                'res_ids': list(records.ids),
            },
        )
        return True

    def trigger_refresh_view(self):
        """ The shortcut method to refresh views that display current recordset
        """
        return self.trigger_refresh_view_for(self)

    def write(self, vals):
        res = super(GenericMixinRefreshView, self).write(vals)

        if not self._auto_refresh_view_on_write:
            return res

        refresh_fields = self._auto_refresh_view_on_field_changes_system()
        if refresh_fields & set(vals):
            self.trigger_refresh_view()
        return res
