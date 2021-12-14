odoo.define('generic_mixin.RefreshViewMixin', function () {
    "use strict";

    var RefreshViewMixin = {
        __refresh_view_mixin: true,
        init: function () {
            this._super.apply(this, arguments);
            this.generic_refresh_view__is_compatible = true;
            this._generic_refresh_mixin__refresh_ids = {};
        },

        generic_refresh_view__set_refresh_ids: function (refresh_ids) {
            if (refresh_ids) {
                this._generic_refresh_mixin__refresh_ids = refresh_ids;
            }
        },

        generic_refresh_view__clear_refresh_ids: function () {
            this._generic_refresh_mixin__refresh_ids = {};
        },
    };

    return RefreshViewMixin;
});
