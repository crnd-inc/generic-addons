/** @odoo-module **/

const RefreshViewMixin = {
    __refresh_view_mixin: true,
    init: function () {
        this._super.apply(this, arguments);
        this.gmrvIsCompatible = true;
        this._gmrvRefreshIds = {};
    },

    gmrvSetRefreshIds: function (refreshIds) {
        if (refreshIds) {
            this._gmrvRefreshIds = refreshIds;
        }
    },

    gmrvClearRefreshIds: function () {
        this._gmrvRefreshIds = {};
    },
};

export default RefreshViewMixin;
