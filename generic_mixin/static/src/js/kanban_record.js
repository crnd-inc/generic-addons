/** @odoo-module **/

import KanbanRecord from 'web.KanbanRecord';

KanbanRecord.include({

    init: function () {
        this._super.apply(this, arguments);
        this._gmrvVisualizationOnTimeout = 100;
        this._gmrvVisualizationOffTimeout = 1200;
    },

    _render: function () {
        var render = this._super.apply(this, arguments);
        this._generic_mixin_refresh_view__visualize_changes(this.$el, this.state.gmrvVisualize);
        return render;
    },

    _generic_mixin_refresh_view__visualize_changes: function ($el, visualize) {
        if (visualize) {
            if (visualize === 'create') {
                setTimeout(() => {
                    $el.addClass('gmrv_highlighting_record_create');
                }, this._gmrvVisualizationOnTimeout);
                setTimeout(() => {
                    $el.removeClass('gmrv_highlighting_record_create');
                }, this._gmrvVisualizationOffTimeout);
            } else if (visualize === 'write') {
                setTimeout(() => {
                    $el.addClass('gmrv_highlighting_record_write');
                }, this._gmrvVisualizationOnTimeout);
                setTimeout(() => {
                    $el.removeClass('gmrv_highlighting_record_write');
                }, this._gmrvVisualizationOffTimeout);
            }
        }
    },
});
