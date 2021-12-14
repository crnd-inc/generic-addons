odoo.define('generic_mixin.ListRenderer', function (require) {
    "use strict";

    var RefreshViewMixin = require('generic_mixin.RefreshViewMixin');

    require('web.ListRenderer').include(RefreshViewMixin);

    require('web.ListRenderer').include({

        init: function () {
            this._super.apply(this, arguments);
            this._generic_refresh_mixin__visualization_on_timeout = 100;
            this._generic_refresh_mixin__visualization_off_timeout = 1200;
        },

        _renderRows: function () {
            var rows = this._super.apply(this, arguments);
            this.generic_refresh_view__clear_refresh_ids();
            return rows;
        },

        _renderRow: function (record) {
            var $tr = this._super.apply(this, arguments);
            this._generic_mixin_refresh_view__visualize_changes(
                $tr, record.res_id);
            return $tr;
        },

        _generic_mixin_refresh_view__visualize_changes: function (
            $tr, res_id) {
            if (this._generic_refresh_mixin__refresh_ids.create &&
                this._generic_refresh_mixin__refresh_ids.write) {
                if (this._generic_refresh_mixin__refresh_ids.create.includes(
                    res_id)) {
                    setTimeout(function () {
                        $tr.addClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_on_timeout);
                    setTimeout(function () {
                        $tr.removeClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_off_timeout);
                } else if (this._generic_refresh_mixin__refresh_ids.write
                    .includes(res_id)) {
                    setTimeout(function () {
                        $tr.addClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__visualization_on_timeout);
                    setTimeout(function () {
                        $tr.removeClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__visualization_off_timeout);
                }
            }
        },
    });
});
