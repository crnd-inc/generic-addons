import { KanbanController } from '@web/views/kanban/kanban_controller';
import { patch } from "@web/core/utils/patch";
import { updateGetLocalStateFunction } from "./gmrv_controller_mixin";

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        updateGetLocalStateFunction(this.model);
    },
});
