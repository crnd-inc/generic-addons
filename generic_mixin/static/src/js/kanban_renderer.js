odoo.define('generic_mixin.KanbanRenderer', function (require) {
    "use strict";

    var RefreshViewMixin = require('generic_mixin.RefreshViewMixin');

    require('web.KanbanRenderer').include(RefreshViewMixin);

    require('web.KanbanRenderer').include({
        _renderView: function () {
            var self = this;
            _.each(self.state.data, function (record) {
                if (self._generic_refresh_mixin__refresh_ids.create &&
                    self._generic_refresh_mixin__refresh_ids.write) {
                    if (self._generic_refresh_mixin__refresh_ids.create
                        .includes(record.res_id)) {
                        record.generic_refresh_view__visualize = 'create';
                    } else if (self._generic_refresh_mixin__refresh_ids.write
                        .includes(record.res_id)) {
                        record.generic_refresh_view__visualize = 'write';
                    }
                }
            });
            this.generic_refresh_view__clear_refresh_ids();

            return this._super.apply(this, arguments);
        },
    });
});
