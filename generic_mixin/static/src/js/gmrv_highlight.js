/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { reactive } from "@odoo/owl";

// How long the highlighting of refreshed records stays applied.
// Has to be greater than the transition duration defined in
// refresh_view.scss, so that records smoothly fade back to normal look.
const GMRV_HIGHLIGHT_DURATION = 1200;

// Shared reactive store of recently refreshed records.
// Structure: {'model.name': {'create': [id1], 'write': [id2]}}
// It is filled in by the WebClient right before reloading the view and read
// by renderers, to highlight records that were just created or updated.
// Renderers have to subscribe to it via 'useState', thus they are
// re-rendered when the store is cleared and highlighting is removed.
export const gmrvHighlightStore = reactive({ records: {} });

let gmrvClearTimer = null;

/** Highlight records listed in 'refreshIds' for a short period of time
 *
 * @param {Object} refreshIds {'model.name': {'create': [], 'write': []}}
 */
export function gmrvSetHighlight(refreshIds) {
    gmrvHighlightStore.records = refreshIds || {};
    if (gmrvClearTimer) {
        browser.clearTimeout(gmrvClearTimer);
    }
    gmrvClearTimer = browser.setTimeout(() => {
        gmrvClearTimer = null;
        gmrvHighlightStore.records = {};
    }, GMRV_HIGHLIGHT_DURATION);
}

/** Compute css class to highlight the record (if it has to be highlighted)
 *
 * @param {Object} store the store, subscribed to via 'useState'
 * @param {String} resModel name of the model of the record
 * @param {Number} resId ID of the record
 * @returns {String} css class name or empty string
 */
export function gmrvGetHighlightClass(store, resModel, resId) {
    if (!resId) {
        return "";
    }
    const modelData = store.records[resModel];
    if (!modelData) {
        return "";
    }
    if (modelData.create && modelData.create.includes(resId)) {
        return "gmrv_highlighting_record_create";
    }
    if (modelData.write && modelData.write.includes(resId)) {
        return "gmrv_highlighting_record_write";
    }
    return "";
}
