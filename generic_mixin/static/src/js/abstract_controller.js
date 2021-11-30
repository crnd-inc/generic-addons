odoo.define('generic_mixin.AbstractController', function (require) {
    "use strict";

    require('web.AbstractController').include({

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);

            this.generic_mixin__is_multi_record =
                params.generic_mixin__is_multi_record;
        },
    });
});
