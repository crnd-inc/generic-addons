odoo.define('generic_mixin.RefreshViewMixin', function (require) {
    "use strict";

    var RefreshViewMixin = {
        __refresh_view_mixin: true,
        init: function () {
            this._super.apply(this, arguments);
            this.generic_refresh_mixin__refresh_ids = {};
            this._generic_refresh_mixin__visualization_on_timeout = 100;
            this._generic_refresh_mixin__visualization_off_timeout = 1200;
        },

        _generic_refresh_view__set_refresh_ids: function (refresh_ids) {
            if (refresh_ids) {
                this.generic_refresh_mixin__refresh_ids = refresh_ids;
            }
        },

        _generic_refresh_view__clear_refresh_ids: function () {
            this.generic_refresh_mixin__refresh_ids = {};
        },

        _generic_mixin_refresh_view_visualize_list_row: function ($tr, res_id) {
            if (this.generic_refresh_mixin__refresh_ids.create &&
                this.generic_refresh_mixin__refresh_ids.write) {
                if (this.generic_refresh_mixin__refresh_ids.create.includes(
                    res_id)) {
                    setTimeout(function () {
                        $tr.addClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_on_timeout);
                    setTimeout(function () {
                        $tr.removeClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_off_timeout);
                } else if (this.generic_refresh_mixin__refresh_ids.write
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
