/** @odoo-module **/

import { useSetupView } from "@web/views/view_hook";

export function updateGetLocalStateFunction(model) {
    useSetupView({
        getLocalState: () => ({ model }),
    });
}
