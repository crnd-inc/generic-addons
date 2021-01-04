odoo.define('generic_mixin.WebClient', function (require) {
    "use strict";

    require('web.WebClient').include({

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

        _generic_mixin_refresh_view_handle: function (message) {
            var self = this;
            var refresh_model = message.model;
            var refresh_ids = message.res_ids;

            var cur_action = self.action_manager.getCurrentAction();
            if (!cur_action || cur_action.res_model !== refresh_model) {
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

            if (cur_action.env.currentId) {
                active_ids.push(cur_action.env.currentId);
            }
            if (!_.isEmpty(cur_action.env.ids)) {
                active_ids = _.union(active_ids, cur_action.env.ids);
            }

            if (_.intersection(refresh_ids, active_ids)) {
                // TODO: think about using 'debounce' or 'throttle' to avoid
                //       too frequent refreshes for view
                _.delay(
                    function (controller) {
                        if (controller && controller.widget) {
                            controller.widget.reload();
                        }
                    },
                    2000,
                    cur_ctl);
            }
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


