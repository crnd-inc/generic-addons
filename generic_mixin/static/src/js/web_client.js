odoo.define('generic_mixin.WebClient', function (require) {
    "use strict";

    require('web.WebClient').include({

        init: function () {
            var self = this;
            self._super.apply(self, arguments);

            // Variable to store pending refreshes
            // Structure:  {'model.name': [id1, id2, id3]}
            // Will be cleaned up on next refresh
            self._generic_refresh_mixin__pending = {};
            self._generic_refresh_mixin__throttle_timeout = 2000;

            // Throttled function to execute only once in
            // throttle timeout time
            self._generic_refresh_mixin__refresher = _.throttle(function () {
                self._generic_mixin_refresh_view__do_refresh();
            }, self._generic_refresh_mixin__throttle_timeout);
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
            if (ctl.widget.mode !== 'readonly') {
                return false;
            }

            var active_ids = [];
            if (act.res_id) {
                active_ids.push(act.res_id);
            }

            if (ctl.widget.initialState) {
                active_ids = _.union(
                    active_ids, ctl.widget.initialState.res_ids);
            }
            if (_.intersection(refresh_ids, active_ids)) {
                return true;
            }
        },

        // Refresh controller
        // :param Controller ctl: controlelr to check
        _generic_mixin_refresh_view__do_refresh_ctl: function (ctl) {
            if (ctl && ctl.widget) {
                var old_dis_autofocus = ctl.widget.disableAutofocus;
                if ('disableAutofocus' in ctl.widget) {
                    // In case of it is form view and has 'disableAutofocus'
                    // property, we have to set it to True, to ensure,
                    // that after update form will not scroll to the top.
                    // This helps a lot in case of frequent (1/sec) refresh
                    // events for the model
                    ctl.widget.disableAutofocus = true;
                    ctl.widget.reload().then(function () {
                        ctl.widget.disableAutofocus = old_dis_autofocus;
                    });
                } else {
                    // Otherwise, simply reload widget
                    ctl.widget.reload();
                }
            }
        },

        _generic_mixin_refresh_view__do_refresh: function () {
            var self = this;
            var cur_ctl = self.action_manager.getCurrentController();
            if (self._generic_mixin_refresh_view__do_refresh_check(cur_ctl)) {
                // Refresh current controller
                self._generic_mixin_refresh_view__do_refresh_ctl(cur_ctl);
            }
            var diag_ctl = self.action_manager.currentDialogController;
            if (self._generic_mixin_refresh_view__do_refresh_check(diag_ctl)) {
                // Refresh current dialog controller
                self._generic_mixin_refresh_view__do_refresh_ctl(diag_ctl);
            }
        },

        _generic_mixin_refresh_view_handle: function (message) {
            var self = this;
            var res_model = message.model;
            var res_ids = message.res_ids;

            if (res_model in self._generic_refresh_mixin__pending) {
                self._generic_refresh_mixin__pending[res_model] = _.union(
                    self._generic_refresh_mixin__pending[res_model],
                    res_ids);
            } else {
                self._generic_refresh_mixin__pending[res_model] = res_ids;
            }
            self._generic_refresh_mixin__refresher();
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
        },
    });
});


