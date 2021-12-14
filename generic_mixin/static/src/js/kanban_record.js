odoo.define('generic_mixin.KanbanRecord', function (require) {
    "use strict";

    require('web.KanbanRecord').include({

        init: function () {
            this._super.apply(this, arguments);
            this._generic_refresh_mixin__visualization_on_timeout = 100;
            this._generic_refresh_mixin__visualization_off_timeout = 1200;
        },

        _render: function () {
            var render = this._super.apply(this, arguments);
            this._generic_mixin_refresh_view__visualize_changes(
                this.$el, this.state.generic_refresh_view__visualize);
            return render;
        },

        _generic_mixin_refresh_view__visualize_changes: function (
            $el, visualize) {
            if (visualize) {
                if (visualize === 'create') {
                    setTimeout(function () {
                        $el.addClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_on_timeout);
                    setTimeout(function () {
                        $el.removeClass('gmrv_highlighting_record_create');
                    }, this._generic_refresh_mixin__visualization_off_timeout);
                } else if (visualize === 'write') {
                    setTimeout(function () {
                        $el.addClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__visualization_on_timeout);
                    setTimeout(function () {
                        $el.removeClass('gmrv_highlighting_record_write');
                    }, this._generic_refresh_mixin__visualization_off_timeout);
                }
            }
        },
    });
});
