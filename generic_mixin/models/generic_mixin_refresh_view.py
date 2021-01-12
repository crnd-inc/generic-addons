import logging
from odoo import models, api

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

        if self._auto_refresh_view_on_write:
            self.trigger_refresh_view()
        return res
