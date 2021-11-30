odoo.define('generic_mixin.AbstractView', function (require) {
    "use strict";

    require('web.AbstractView').include({

        init: function () {
            this._super.apply(this, arguments);

            this.controllerParams.isMultiRecord = this.multi_record;
        },
    });
});
