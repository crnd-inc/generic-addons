odoo.define('generic_mixin.ListRenderer', function (require) {
    "use strict";

    require('web.ListRenderer').include({

        init: function () {
            this._super.apply(this, arguments);
            this.generic_refresh_mixin__refresh_ids = {};
            this._generic_refresh_mixin__highlighting_on_timeout = 100;
            this._generic_refresh_mixin__highlighting_off_timeout = 1200;
        },

        _renderRows: function () {
            var rows = this._super.apply(this, arguments);
            this.generic_refresh_mixin__refresh_ids = {};
            return rows;
        },

        _renderRow: function (record) {
            var $tr = this._super.apply(this, arguments);

            if (this.generic_refresh_mixin__refresh_ids.create &&
                this.generic_refresh_mixin__refresh_ids.write) {
                if (this.generic_refresh_mixin__refresh_ids.create.includes(
                    record.res_id)) {
                    setTimeout(function () {
                        $tr.addClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__highlighting_on_timeout);
                    setTimeout(function () {
                        $tr.removeClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__highlighting_off_timeout);
                } else if (this.generic_refresh_mixin__refresh_ids.write
                    .includes(record.res_id)) {
                    setTimeout(function () {
                        $tr.addClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__highlighting_on_timeout);
                    setTimeout(function () {
                        $tr.removeClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__highlighting_off_timeout);
                }
            }

            return $tr;
        },
    });
});
