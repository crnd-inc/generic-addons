/** @odoo-module **/

import concurrency from 'web.concurrency';
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";

patch(
    WebClient.prototype,
    'Add refresh view after changed on the records',
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
        },

        mounted() {
            this._super(...arguments);
            let busService = useService('bus_service');
            busService.addChannel('generic_mixin_refresh_view');
            busService.onNotification(
                null, this._onBusGMRVNotification.bind(this));
        },

        _gmrvDoRefreshCheck (controller) {
            if (controller.view.isLegacy) {
                return this._gmrvDoRefreshCheckLegacy(controller);
            }

            return  false;
        },

        _gmrvDoRefreshCheckLegacy (controller) {
            if (!controller) {
                return false;
            }

            if (!controller.action) {
                return false;
            }

            let refreshIds = this._gmrvPending[controller.action.res_model];
            if (!refreshIds) {
                return false;
            }

            let actions = this._gmrvPendingAction[controller.action.res_model];
            if (!actions) {
                return false;
            }

            let localState = controller.getLocalState();
            if (localState.__legacy_widget__.mode !== 'readonly') {
                return false;
            }

            if (controller.view.multiRecord &&
                (actions.includes('create') || actions.includes('unlink'))) {
                // Always refresh multirecord view on create or unlink.
                // There is no need to compare changed ids and displayed ids
                // in this case.
                return true;
            }

            // Find ids of records displayed by current action
            let activeIds = [];
            if (controller.action.res_id) {
                activeIds.push(controller.action.res_id);
            }

            let globalState = controller.getGlobalState();
            if (!controller.view.multiRecord && localState.currentId) {
                activeIds = [
                    ...new Set([
                        ...activeIds,
                        ...[localState.currentId],
                    ]),
                ];
            } else if (controller.view.multiRecord && globalState.resIds) {
                activeIds = [
                    ...new Set([
                        ...activeIds,
                        ...globalState.resIds,
                    ]),
                ];
            }

            if (activeIds.filter(e => refreshIds.includes(e)).length) {
                return true;
            }

            return false;
        },

        _gmrvDoRefreshController (controller) {
            if (controller.view.isLegacy) {
                return this._gmrvDoRefreshControllerLegacy(controller);
            }
        },
        /* eslint-enable complexity */

        // Refresh controller
        _gmrvDoRefreshControllerLegacy (controller) {
            let localState = controller.getLocalState();
            if (localState && localState.__legacy_widget__) {
                let widget = localState.__legacy_widget__;
                var oldDisAutofocus = widget.disableAutofocus;

                if (widget.renderer.gmrvIsCompatible) {
                    widget.renderer.gmrvSetRefreshIds(
                        this._gmrvRefreshIds[widget.modelName]);
                }

                if ('disableAutofocus' in widget) {
                    // In case of it is form view and has 'disableAutofocus'
                    // property, we have to set it to True, to ensure,
                    // that after update form will not scroll to the top.
                    // This helps a lot in case of frequent (1/sec) refresh
                    // events for the model
                    widget.disableAutofocus = true;
                    return widget.reload().then(function () {
                        widget.disableAutofocus = oldDisAutofocus;
                    });
                }

                // Otherwise, simply reload widget
                return widget.reload();
            }
        },

        _gmrvDoRefresher () {
            let self = this;
            let currentController = this.actionService.currentController;

            // TODO: user controller's mutext to avoid errors like
            //       'undefined has no attr commitChanges
            this._gmrvMutex.exec(function () {
                var promises = [];
                if (self._gmrvDoRefreshCheck(currentController)) {
                    // Refresh current controller
                    promises.push(
                        self._gmrvDoRefreshController(currentController));
                }

                // Cleanup pending updates
                self._gmrvPending = {};
                self._gmrvPendingAction = {};
                self._gmrvRefreshIds = {};

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

        _onBusGMRVNotification (notifications) {
            notifications.forEach((notif) => {
                if (notif.type === 'generic_mixin_refresh_view') {
                    try {
                        this._gmrvHandle(notif.payload);
                    } catch (e) {
                        console.log("Cannot refresh view", e);
                    }
                }
            });

           if (Object.keys(this._gmrvPendingAction).length) {
               this._gmrvRefresher();
           }
        },
    });
