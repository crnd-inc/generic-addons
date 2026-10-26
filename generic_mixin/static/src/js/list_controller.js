import { ListController } from '@web/views/list/list_controller';
import { patch } from "@web/core/utils/patch";
import { updateGetLocalStateFunction } from "./gmrv_controller_mixin";

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        updateGetLocalStateFunction(this.model);
    },
});
