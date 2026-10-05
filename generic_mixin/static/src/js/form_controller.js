/** @odoo-module **/

import { FormController } from '@web/views/form/form_controller';
import { patch } from "@web/core/utils/patch";
import { updateGetLocalStateFunction } from "./gmrv_controller_mixin";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        updateGetLocalStateFunction(this.model);
    },
});
