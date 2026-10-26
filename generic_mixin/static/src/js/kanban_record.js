import { KanbanRecord } from '@web/views/kanban/kanban_record';
import { patch } from "@web/core/utils/patch";
import { proxy } from "@odoo/owl";
import { gmrvGetHighlightClass, gmrvHighlightStore } from "./gmrv_highlight";

patch(KanbanRecord.prototype, {
    setup() {
        super.setup(...arguments);
        this.gmrvHighlight = proxy(gmrvHighlightStore);
    },

    getCardClasses() {
        const classes = super.getCardClasses(...arguments);
        const { record } = this.props;
        const highlightClass = gmrvGetHighlightClass(
            this.gmrvHighlight, record.resModel, record.resId);
        return highlightClass ? `${classes} ${highlightClass}` : classes;
    },
});
