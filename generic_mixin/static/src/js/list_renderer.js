odoo.define('generic_mixin.ListRenderer', function (require) {
    "use strict";

    var RefreshViewMixin = require('generic_mixin.RefreshViewMixin');

    require('web.ListRenderer').include(RefreshViewMixin);

    require('web.ListRenderer').include({

        _renderRows: function () {
            var rows = this._super.apply(this, arguments);
            this._generic_refresh_view__clear_refresh_ids();
            return rows;
        },

        _renderRow: function (record) {
            var $tr = this._super.apply(this, arguments);
            this._generic_mixin_refresh_view_visualize_list_row(
                $tr, record.res_id);
            return $tr;
        },
    });
});
