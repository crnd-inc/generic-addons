/** @odoo-module **/

import KanbanRenderer from 'web.KanbanRenderer';
import RefreshViewMixin from './refresh_view_mixin';

KanbanRenderer.include(RefreshViewMixin);

KanbanRenderer.include({
    _renderView: function () {
        this.state.data.forEach((record) => {
            if (this._gmrvRefreshIds.create || this._gmrvRefreshIds.write) {
                if (this._gmrvRefreshIds.create .includes(record.res_id)) {
                    record.gmrvVisualize = 'create';
                } else if (this._gmrvRefreshIds.write .includes(record.res_id)) {
                    record.gmrvVisualize = 'write';
                }
            }
        });
        this.gmrvClearRefreshIds();

        return this._super.apply(this, arguments);
    },
});
