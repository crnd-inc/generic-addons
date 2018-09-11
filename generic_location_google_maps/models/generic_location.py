from odoo import api, models, _


class GenericLocation(models.Model):
    _inherit = 'generic.location'

    @api.multi
    def action_button_show_location_map(self):
        action = self.env.ref(
            'generic_location.generic_location_action').read()[0]
        views = []
        map_view = False
        for view_id, view_type in list(action['views']):
            if view_type == 'map':
                map_view = (view_id, view_type)
            else:
                views += [(view_id, view_type)]

        if map_view:
            views.insert(0, map_view)

        action.update({
            'name': _('Map'),
            'display_name': _('Map'),
            'views': views,
            'domain': [('id', '=', self.id)],
        })
        return action
