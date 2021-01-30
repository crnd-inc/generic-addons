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
            self._generic_refresh_mixin__debounce_timeout = 2000;

            // Debounced function to be called not more then onece per 1000 ms
            self._generic_refresh_mixin__refresher = _.debounce(function () {
                self._generic_mixin_refresh_view__do_refresh();
            }, self._generic_refresh_mixin__debounce_timeout);
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

        _generic_mixin_refresh_view__do_refresh: function () {
            var self = this;
            var cur_action = self.action_manager.getCurrentAction();
            if (!cur_action) {
                return;
            }

            var refresh_ids = self._generic_refresh_mixin__pending[
                cur_action.res_model];

            // Clenaup all pending refresh data, before continueing.
            self._generic_refresh_mixin__pending = {};

            if (!refresh_ids) {
                return;
            }

            var cur_ctl = self.action_manager.getCurrentController();
            if (!cur_ctl || cur_ctl.widget.mode !== 'readonly') {
                return;
            }
            var active_ids = [];
            if (cur_action.res_id) {
                active_ids.push(cur_action.res_id);
            }

            if (cur_ctl.widget.initialState) {
                active_ids = _.union(
                    active_ids, cur_ctl.widget.initialState.res_ids);
            }

            if (_.intersection(refresh_ids, active_ids)) {
                if (cur_ctl && cur_ctl.widget) {
                    cur_ctl.widget.reload();
                }
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


