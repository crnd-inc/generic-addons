odoo.define('generic_mixin.WebClient', function (require) {
    "use strict";

    var concurrency = require('web.concurrency');

    require('web.WebClient').include({

        init: function () {
            var self = this;
            self._super.apply(self, arguments);

            // Variable to store pending refreshes
            // Structure:  {'model.name': [id1, id2, id3]}
            // Will be cleaned up on next refresh
            self._generic_refresh_mixin__pending = {};

            // Variable to store pending actions (create, write, unlink)
            // Structure: {'model.name': ['create', 'write']}
            // Will be cleaned on next refresh
            self._generic_refresh_mixin__pending_action = {};

            // Variable to store ids for transmission to ListRenderer
            // Structure: {'model.name': {'create': [id1]}, {'write': [id1]}}
            // Will be cleaned on next refresh
            self._generic_refresh_mixin__refresh_ids = {};

            // Throttle timeout for refresh
            // TODO: first refresh we have to do after 200 ms after message.
            self._generic_refresh_mixin__throttle_timeout = 4000;

            self._generic_refresh_mixin__mutex =
                new concurrency.MutexedDropPrevious();

            // Throttled function to execute only once in
            // throttle timeout time
            self._generic_refresh_mixin__refresher = _.throttle(
                function () {
                    self._generic_mixin_refresh_view__do_refresh();
                },
                self._generic_refresh_mixin__throttle_timeout,
                {'leading': false});
        },

        show_application: function () {
            var shown = this._super(this, arguments);

            // Register channeld for refresh events
            this.call(
                'bus_service', 'addChannel', 'generic_mixin_refresh_view');

            // Register notification handler
            this.call('bus_service', 'onNotification',
                this, this.onBusGMRVNotification);
            return shown;
        },

        // Check if need to update controller
        // :param Controller ctl: controlelr to check
        _generic_mixin_refresh_view__do_refresh_check: function (ctl) {
            var self = this;
            if (!ctl) {
                return false;
            }

            var act = self.action_manager.actions[ctl.actionID];
            if (!act) {
                return false;
            }

            var refresh_ids = self._generic_refresh_mixin__pending[
                act.res_model];
            if (!refresh_ids) {
                return false;
            }

            var actions =
                self._generic_refresh_mixin__pending_action[
                    act.res_model];
            if (!actions) {
                return false;
            }

            if (ctl.widget.mode !== 'readonly') {
                return false;
            }

            if (ctl.widget.isMultiRecord &&
                (actions.includes('create') || actions.includes('unlink'))) {
                // Always refresh multirecord view on create or unlink.
                // There is no need to compare changed ids and displayed ids
                // in this case.
                return true;
            }

            // Find ids of records displayed by current action
            var active_ids = [];
            if (act.res_id) {
                active_ids.push(act.res_id);
            }

            if (act.env.currentId) {
                active_ids.push(act.env.currentId);
            } else if (!_.isEmpty(act.env.ids)) {
                active_ids = _.union(active_ids, act.env.ids);
            }

            if (!_.isEmpty(_.intersection(refresh_ids, active_ids))) {
                // Need refresh only is refreshed id is displayed in the view.
                // This is true for both, write and unlink operation.
                return true;
            }

            return false;
        },

        // Refresh controller
        // :param Controller ctl: controlelr to check
        _generic_mixin_refresh_view__do_refresh_ctl: function (ctl) {
            if (ctl && ctl.widget) {
                var old_dis_autofocus = ctl.widget.disableAutofocus;

                if (ctl.widget.renderer.generic_refresh_view__is_compatible) {
                    var refresh_ids = this._generic_refresh_mixin__refresh_ids[
                        ctl.widget.modelName];
                    ctl.widget.renderer.generic_refresh_view__set_refresh_ids(
                        refresh_ids);
                }

                if ('disableAutofocus' in ctl.widget) {
                    // In case of it is form view and has 'disableAutofocus'
                    // property, we have to set it to True, to ensure,
                    // that after update form will not scroll to the top.
                    // This helps a lot in case of frequent (1/sec) refresh
                    // events for the model
                    ctl.widget.disableAutofocus = true;
                    return ctl.widget.reload().then(function () {
                        ctl.widget.disableAutofocus = old_dis_autofocus;
                    });
                }

                // Otherwise, simply reload widget
                return ctl.widget.reload();
            }
        },

        _generic_mixin_refresh_view__do_refresh: function () {
            var self = this;

            var cur_ctl = self.action_manager.getCurrentController();
            self._generic_refresh_mixin__mutex.exec(function () {
                var promises = [];
                if (self._generic_mixin_refresh_view__do_refresh_check(
                    cur_ctl)) {
                    // Refresh current controller
                    promises.push(
                        self._generic_mixin_refresh_view__do_refresh_ctl(
                            cur_ctl));
                }
                var diag_ctl = self.action_manager.currentDialogController;
                if (self._generic_mixin_refresh_view__do_refresh_check(
                    diag_ctl)) {
                    // Refresh current dialog controller
                    promises.push(
                        self._generic_mixin_refresh_view__do_refresh_ctl(
                            diag_ctl)
                    );
                }
                // Cleanup pending updates
                self._generic_refresh_mixin__pending = {};
                self._generic_refresh_mixin__pending_action = {};
                self._generic_refresh_mixin__refresh_ids = {};
                return $.when.apply($, promises);
            });
        },

        // Param message: object/dict with following format:
        // {
        //     'res_model': {
        //         'action': [res_ids],
        //     },
        // }
        _generic_mixin_refresh_view_handle: function (message) {
            var self = this;
            _.each(message, function (action_data, res_model) {
                _.each(action_data, function (res_ids, action) {
                    // Store changed ids
                    if (res_model in self._generic_refresh_mixin__pending) {
                        self._generic_refresh_mixin__pending[res_model] =
                            _.union(
                                self._generic_refresh_mixin__pending[res_model],
                                res_ids);
                    } else {
                        self._generic_refresh_mixin__pending[res_model] =
                            res_ids;
                    }

                    // Store received action
                    if (res_model in
                        self._generic_refresh_mixin__pending_action) {
                        self._generic_refresh_mixin__pending_action[res_model] =
                            _.union(
                                self._generic_refresh_mixin__pending_action[
                                    res_model],
                                [action]);
                    } else {
                        self._generic_refresh_mixin__pending_action[res_model] =
                            [action];
                    }

                    // Store changed ids for ListRenderer
                    if (action !== 'unlink') {
                        if (!(res_model in
                            self._generic_refresh_mixin__refresh_ids)) {
                            self._generic_refresh_mixin__refresh_ids[
                                res_model] = {
                                create: [],
                                write: [],
                            };
                        }
                        self._generic_refresh_mixin__refresh_ids[
                            res_model][action] =
                            _.union(
                                self._generic_refresh_mixin__refresh_ids[
                                    res_model][action],
                                res_ids);
                    }
                });
            });
        },

        // The GMRV infix in name is used to avoid possible name conflicts
        onBusGMRVNotification: function (notifications) {
            var self = this;
            _.each(notifications, function (notif) {
                if (notif[0] === 'generic_mixin_refresh_view') {
                    try {
                        self._generic_mixin_refresh_view_handle(notif[1]);
                    } catch (e) {
                        console.log("Cannot refresh view", e);
                    }
                }
            });

            if (!_.isEmpty(self._generic_refresh_mixin__pending_action)) {
                self._generic_refresh_mixin__refresher();
            }
        },
    });
});


