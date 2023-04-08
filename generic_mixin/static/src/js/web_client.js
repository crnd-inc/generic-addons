/** @odoo-module **/

import concurrency from 'web.concurrency';
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

const GMRV_NAME = 'generic_mixin_refresh_view';

patch(
    WebClient.prototype,
    'generix_mixin',
    {
        setup() {
            this._super(...arguments);

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
            this._gmrvMutex = new concurrency.MutexedDropPrevious();

            // Throttled function to execute only once in
            // throttle timeout time
            this._gmrvRefresher = _.throttle(
                this._gmrvDoRefresher.bind(this),
                4000,
                {'leading': false},
            );

            this.env.services['bus_service'].addChannel(GMRV_NAME);
            this.env.services['bus_service'].addEventListener(
                'notification', this._onBusGMRVNotification.bind(this));
        },

        _gmrvDoRefreshCheck (controller) {
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

            const localState = controller.getLocalState();
            const modelRoot = localState.model?.root;
            if (!modelRoot || modelRoot.isDirty || modelRoot.isVirtual) {
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
        /* eslint-enable complexity */

        // Refresh controller
        _gmrvDoRefreshController (controller) {
            const localState = controller.getLocalState();
            const params = {};
            if (controller.view?.type === 'form' && localState.resId) {
                params.resId = localState.resId;
            }
            localState.model.load(params);
        },

        _gmrvDoRefresher () {
            let currentController = this.actionService.currentController;

            // TODO: user controller's mutext to avoid errors like
            //       'undefined has no attr commitChanges
            this._gmrvMutex.exec(() => {
                const promises = [];
                if (this._gmrvDoRefreshCheck(currentController)) {
                    // Refresh current controller
                    promises.push(
                        this._gmrvDoRefreshController(currentController));
                }

                // Cleanup pending updates
                this._gmrvPending = {};
                this._gmrvPendingAction = {};
                this._gmrvRefreshIds = {};

                return Promise.all(promises);
            });
        },

        _gmrvHandle (message) {
            for (let [resModel, actionData] of Object.entries(message)) {
                for (let [action, resIds] of Object.entries(actionData)) {
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

        _onBusGMRVNotification (event) {
            const gmrvNotifications = event.detail.filter(e => e.type === GMRV_NAME);
            if (!gmrvNotifications.length) {
                return;
            }
            gmrvNotifications.forEach((notif) => {
                try {
                    this._gmrvHandle(notif.payload);
                } catch (e) {
                    console.log("Cannot refresh view", e);
                }
            });

           if (Object.keys(this._gmrvPendingAction).length) {
               this._gmrvRefresher();
           }
        },
    },
);
