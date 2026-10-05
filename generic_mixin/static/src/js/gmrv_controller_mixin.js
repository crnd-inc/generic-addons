/** @odoo-module **/

import { useSetupAction } from "@web/search/action_hook";

export function updateGetLocalStateFunction(model) {
    // Since Odoo 17 'useSetupView' hook was replaced with 'useSetupAction'
    useSetupAction({
        getLocalState: () => ({ model }),
    });
}
