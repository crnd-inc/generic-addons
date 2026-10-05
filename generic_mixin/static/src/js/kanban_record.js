/** @odoo-module **/

import { KanbanRecord } from '@web/views/kanban/kanban_record';
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { gmrvGetHighlightClass, gmrvHighlightStore } from "./gmrv_highlight";

patch(KanbanRecord.prototype, {
    setup() {
        super.setup(...arguments);
        this.gmrvHighlight = useState(gmrvHighlightStore);
    },

    getRecordClasses() {
        const classes = super.getRecordClasses(...arguments);
        const { record } = this.props;
        const highlightClass = gmrvGetHighlightClass(
            this.gmrvHighlight, record.resModel, record.resId);
        return highlightClass ? `${classes} ${highlightClass}` : classes;
    },
});
