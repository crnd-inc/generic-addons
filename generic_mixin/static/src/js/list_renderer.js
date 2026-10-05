/** @odoo-module **/

import { ListRenderer } from '@web/views/list/list_renderer';
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { gmrvGetHighlightClass, gmrvHighlightStore } from "./gmrv_highlight";

patch(ListRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.gmrvHighlight = useState(gmrvHighlightStore);
    },

    getRowClass(record) {
        const classNames = super.getRowClass(...arguments);
        const highlightClass = gmrvGetHighlightClass(
            this.gmrvHighlight, this.props.list.resModel, record.resId);
        return highlightClass ? `${classNames} ${highlightClass}` : classNames;
    },
});
