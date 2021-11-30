odoo.define('generic_mixin.AbstractView', function (require) {
    "use strict";

    require('web.AbstractView').include({

        init: function () {
            this._super.apply(this, arguments);

            this.controllerParams.generic_mixin__is_multi_record =
                this.multi_record;
        },
    });
});
