/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { KeepLast } from '@web/core/utils/concurrency';
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { gmrvSetHighlight } from "./gmrv_highlight";

const GMRV_NAME = 'generic_mixin_refresh_view';
const GMRV_REFRESH_DELAY = 4000;

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);

        // Variable to store pending refreshes
        // Structure:  {'model.name': [id1, id2, id3]}
        // Will be cleaned up on next refresh
        this._gmrvPending = {};
        // Variable to store pending actions (create, write, unlink)
        // Structure: {'model.name': ['create', 'write']}
        // Will be cleaned on next refresh
        this._gmrvPendingAction = {};
        // Variable to store ids for transmission to ListRenderer
        // Structure: {'model.name': {'create': [id1]}, {'write': [id1]}}
        // Will be cleaned on next refresh
        this._gmrvRefreshIds = {};
        this._gmrvKeepLast = new KeepLast();
        // Timer id of the scheduled refresh. Used to throttle refreshes:
        // all notifications received within GMRV_REFRESH_DELAY are handled
        // by a single refresh, that is executed at the end of that period.
        this._gmrvRefreshTimer = null;

        // Since Odoo 17 notifications are dispatched per notification type
        // via 'subscribe'. There is no generic 'notification' event anymore.
        this.env.services.bus_service.subscribe(
            GMRV_NAME, this._onBusGMRVNotification.bind(this));
        this.env.services.bus_service.addChannel(GMRV_NAME);
    },

    /** Schedule a single refresh for all notifications received recently */
    _gmrvRefresher() {
        if (this._gmrvRefreshTimer) {
            return;
        }
        this._gmrvRefreshTimer = browser.setTimeout(() => {
            this._gmrvRefreshTimer = null;
            this._gmrvDoRefresher();
        }, GMRV_REFRESH_DELAY);
    },

    async _gmrvDoRefreshCheck(controller) {
        if (!controller) {
            return false;
        }

        if (!controller.action) {
            return false;
        }

        const refreshIds = this._gmrvPending[controller.action.res_model];
        if (!refreshIds) {
            return false;
        }

        const actions = this._gmrvPendingAction[controller.action.res_model];
        if (!actions) {
            return false;
        }

        const localState = controller.getLocalState?.();
        const modelRoot = localState?.model?.root;
        if (!modelRoot || modelRoot.isNew) {
            return false;
        }
        // Since Odoo 17 'isDirty' is an async method instead of a property
        if (modelRoot.isDirty && await modelRoot.isDirty()) {
            return false;
        }

        const isMultiRecord = controller.view.multiRecord;
        if (isMultiRecord &&
            (actions.includes('create') || actions.includes('unlink'))) {
            // Always refresh multirecord view on create or unlink.
            // There is no need to compare changed ids and displayed ids
            // in this case.
            return true;
        }

        // Find ids of records displayed by current action
        let activeIds = [];
        if (isMultiRecord) {
            activeIds = modelRoot.records.map(e => e.resId);
        } else {
            activeIds.push(modelRoot.resId);
        }

        return !!activeIds.filter(e => refreshIds.includes(e)).length;
    },

    _gmrvDoRefreshController(controller) {
        const localState = controller.getLocalState();
        const params = {};
        if (controller.view?.type === 'form' && localState.resId) {
            params.resId = localState.resId;
        }
        return localState.model.load(params);
    },

    _gmrvDoRefresher() {
        const currentController = this.actionService.currentController;

        return this._gmrvKeepLast.add((async () => {
            if (await this._gmrvDoRefreshCheck(currentController)) {
                // Pass changed ids to renderers before the reload, thus
                // created/updated records are highlighted on re-render
                gmrvSetHighlight(this._gmrvRefreshIds);

                // Refresh current controller
                await this._gmrvDoRefreshController(currentController);
            }

            // Cleanup pending updates
            this._gmrvPending = {};
            this._gmrvPendingAction = {};
            this._gmrvRefreshIds = {};
        })());
    },

    _gmrvHandle(message) {
        for (const [resModel, actionData] of Object.entries(message)) {
            for (const [action, resIds] of Object.entries(actionData)) {
                // Store changed ids
                if (resModel in this._gmrvPending) {
                    this._gmrvPending[resModel] = [
                        ...new Set([
                            ...this._gmrvPending[resModel],
                            ...resIds,
                        ]),
                    ];
                } else {
                    this._gmrvPending[resModel] = resIds;
                }

                // Store received action
                if (resModel in this._gmrvPendingAction) {
                    this._gmrvPendingAction[resModel] = [
                        ...new Set([
                            ...this._gmrvPendingAction[resModel],
                            ...[action],
                        ]),
                    ];
                } else {
                    this._gmrvPendingAction[resModel] = [action];
                }

                // Store changed ids for ListRenderer
                if (action !== 'unlink') {
                    if (!(resModel in this._gmrvRefreshIds)) {
                        this._gmrvRefreshIds[resModel] = {
                            create: [],
                            write: [],
                        };
                    }
                    this._gmrvRefreshIds[resModel][action] = [
                        ...new Set([
                            ...this._gmrvRefreshIds[resModel][action],
                            ...resIds,
                        ]),
                    ];
                }
            }
        }
    },

    _onBusGMRVNotification(payload) {
        try {
            this._gmrvHandle(payload);
        } catch (e) {
            console.warn("Cannot refresh view", e);
            return;
        }

        if (Object.keys(this._gmrvPendingAction).length) {
            this._gmrvRefresher();
        }
    },
});
