/** @odoo-module **/

import ListRenderer from 'web.ListRenderer';
import RefreshViewMixin from './refresh_view_mixin';

ListRenderer.include(RefreshViewMixin);

ListRenderer.include({
   init: function () {
       this._super.apply(this, arguments);
       this._gmrvVisualizationOnTimeout = 100;
       this._gmrvVisualizationOffTimeout = 1200;
   },

    _renderRows: function () {
        let rows = this._super.apply(this, arguments);
        this.gmrvClearRefreshIds();
        return rows;
    },

    _renderRow: function (record) {
        let $tr = this._super.apply(this, arguments);
        this.gmrvVisualizeListRowChanges($tr, record.res_id);
        return $tr;
    },

    gmrvVisualizeListRowChanges: function ($tr, resId) {
        if (this._gmrvRefreshIds.create && this._gmrvRefreshIds.write) {
            if (this._gmrvRefreshIds.create.includes(resId)) {
                setTimeout(function () {
                    $tr.addClass('gmrv_highlighting_record_create');
                }, this._gmrvVisualizationOnTimeout);
                setTimeout(function () {
                    $tr.removeClass('gmrv_highlighting_record_create');
                }, this._gmrvVisualizationOffTimeout);
            } else if (this._gmrvRefreshIds.write.includes(resId)) {
                setTimeout(function () {
                    $tr.addClass('gmrv_highlighting_record_write');
                }, this._gmrvVisualizationOnTimeout);
                setTimeout(function () {
                    $tr.removeClass('gmrv_highlighting_record_write');
                }, this._gmrvVisualizationOffTimeout);
            }
        }
    },
});
