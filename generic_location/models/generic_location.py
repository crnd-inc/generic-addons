import logging
from psycopg2 import sql
from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'mail.thread',
        'generic.mixin.parent.names',
    ]
    _parent_name = 'parent_id'
    _parent_store = True
    _description = 'Location'

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    parent_id = fields.Many2one(
        'generic.location', index=True, ondelete='cascade',
        string='Parent Location')
    parent_path = fields.Char(index=True)
    parent_ids = fields.Many2manyView(
        comodel_name='generic.location',
        relation='generic_location_parents_rel_view',
        column1='child_id',
        column2='parent_id',
        string='Parents',
        readonly=True)

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

    @api.model_cr
    def init(self):
        # Create relation (location_id <-> parent_location_id) as PG View
        # This relation is used to compute field parent_ids

        tools.drop_view_if_exists(
            self.env.cr, 'generic_location_parents_rel_view')
        self.env.cr.execute(sql.SQL("""
            CREATE or REPLACE VIEW generic_location_parents_rel_view AS (
                SELECT c.id AS child_id,
                       p.id AS parent_id
                FROM generic_location AS c
                LEFT JOIN generic_location AS p ON (
                    p.id::character varying IN (
                        SELECT * FROM unnest(regexp_split_to_array(
                            c.parent_path, '/')))
                    AND p.id != c.id)
            )
        """))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        res = super(GenericLocation, self).create(vals)

        # Invalidate cache for 'parent_ids' field
        if 'parent_id' in vals:
            self.invalidate_cache(['parent_ids'])
        return res

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(GenericLocation, self).write(vals)

        # Invalidate cache for 'parent_ids' field
        if 'parent_id' in vals:
            self.invalidate_cache(['parent_ids'])
        return res

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
