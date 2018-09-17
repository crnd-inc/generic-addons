from odoo import models, fields, api, tools, _

import logging
_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'mail.thread',
        'generic.mixin.parent.names',
    ]
    _parent_name = 'parent_id'
    _description = 'Location'

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    parent_id = fields.Many2one(
        'generic.location', index=True, string='Parent Location')
    active = fields.Boolean(default=True, index=True)
    child_ids = fields.One2many(
        'generic.location', 'parent_id', string='Sublocations', readonly=True)
    child_count = fields.Integer(compute='_compute_child_count', readonly=True)

    # Images
    image = fields.Binary(
        attachment=True,
        help="This field holds the image used as image for the location, "
             "limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the location. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. ")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of the location. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. ")

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         ("The title of the Location should not be the description")),
    ]

    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(GenericLocation, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(GenericLocation, self).write(vals)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', (u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = (u"Copy of {}").format(self.name)
        else:
            new_name = (u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(GenericLocation, self).copy(default)

    @api.multi
    def action_button_show_sublocations(self):
        action = self.env.ref(
            'generic_location.generic_location_action').read()[0]
        action.update({
            'name': _('Sublocations'),
            'display_name': _('Sublocations'),
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
        })
        return action
