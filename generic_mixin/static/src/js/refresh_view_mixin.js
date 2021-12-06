odoo.define('generic_mixin.RefreshViewMixin', function () {
    "use strict";

    var RefreshViewMixin = {
        __refresh_view_mixin: true,
        init: function () {
            this._super.apply(this, arguments);
            this.generic_refresh_view__is_compatible = true;
            this._generic_refresh_mixin__refresh_ids = {};
            this._generic_refresh_mixin__visualization_on_timeout = 100;
            this._generic_refresh_mixin__visualization_off_timeout = 1200;
        },

        generic_refresh_view__set_refresh_ids: function (refresh_ids) {
            if (refresh_ids) {
                this._generic_refresh_mixin__refresh_ids = refresh_ids;
            }
        },

        generic_refresh_view__clear_refresh_ids: function () {
            this._generic_refresh_mixin__refresh_ids = {};
        },

        generic_mixin_refresh_view__visualize_list_row_changes: function (
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
    };

    return RefreshViewMixin;
});
