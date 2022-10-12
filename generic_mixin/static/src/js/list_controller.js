/** @odoo-module **/

import { ListController } from '@web/views/list/list_controller';
import { patch } from "@web/core/utils/patch";
import { updateGetLocalStateFunction } from "./gmrv_controller_mixin";

patch(
    ListController.prototype,
    'generic_mixin',
    {
        setup() {
            this._super(...arguments)
            updateGetLocalStateFunction(this.model);
        },
    },
);
