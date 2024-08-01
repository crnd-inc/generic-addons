import logging
from odoo import models, fields, api, _

from odoo.addons.generic_mixin import post_create, post_write
from odoo.addons.generic_mixin.tools.sql import create_sql_view
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m

from ..tools.utils import l_parent_compute, l_parent_inverse

_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'mail.thread',
        'image.mixin',
        'generic.tag.mixin',
        'generic.mixin.parent.names',
        'generic.mixin.get.action',
        'generic.mixin.track.changes',
    ]
    _parent_name = 'parent_id'
    _parent_store = True
    _description = 'Location'
    _order = 'name ASC, id ASC'

    def _default_country_id(self):
        company = self.env.user.company_id
        return company.country_id

    name = fields.Char(required=True, index=True)
    type_id = fields.Many2one(
        'generic.location.type',
        ondelete='restrict', index=True, tracking=True,
        help="Type of Location")
    description = fields.Text()
    parent_id = fields.Many2one(
        'generic.location', index=True, ondelete='cascade',
        string='Parent Location')
    parent_path = fields.Char(index=True, readonly=True, unaccent=False)
    parent_ids = fields.Many2manyView(
        comodel_name='generic.location',
        relation='generic_location_parents_rel_view',
        column1='child_id',
        column2='parent_id',
        string='Parents',
        readonly=True, copy=False)

    partner_id = fields.Many2one(
        'res.partner', index=True,
        help='Partner / customer related to this location.')

    active = fields.Boolean(default=True, index=True)
    child_ids = fields.One2many(
        'generic.location', 'parent_id', string='Sublocations', readonly=True)
    child_count = fields.Integer(compute='_compute_child_count', readonly=True)
    child_all_ids = fields.Many2manyView(
        comodel_name='generic.location',
        relation='generic_location_parents_rel_view',
        column1='parent_id',
        column2='child_id',
        string='All Childs',
        readonly=True, copy=False)
    child_all_count = fields.Integer(
        compute='_compute_child_all_count', readonly=True)

    street = fields.Char(
        compute=l_parent_compute('street'),
        inverse=l_parent_inverse('street'),
        store=True, recursive=True,
    )
    _street = fields.Char(string="System Street")
    street_use_parent = fields.Boolean(
        string="Use Parent Street"
    )
    street_readonly = fields.Boolean(
        related='street_use_parent', readonly=True)

    street2 = fields.Char(
        compute=l_parent_compute('street2'),
        inverse=l_parent_inverse('street2'),
        store=True, recursive=True,
    )
    _street2 = fields.Char(string="System Street2")
    street2_use_parent = fields.Boolean(
        string="Use Parent Street2"
    )
    street2_readonly = fields.Boolean(
        related='street2_use_parent', readonly=True)

    zip = fields.Char(
        compute=l_parent_compute('zip'),
        inverse=l_parent_inverse('zip'),
        store=True, recursive=True,
    )
    _zip = fields.Char(string="System Zip")
    zip_use_parent = fields.Boolean(
        string="Use Parent Zip"
    )
    zip_readonly = fields.Boolean(
        related='zip_use_parent', readonly=True)

    city = fields.Char(
        compute=l_parent_compute('city'),
        inverse=l_parent_inverse('city'),
        store=True, recursive=True,
    )
    _city = fields.Char(string="System City")
    city_use_parent = fields.Boolean(
        string="Use Parent City"
    )
    city_readonly = fields.Boolean(
        related='city_use_parent', readonly=True)

    state_id = fields.Many2one(
        'res.country.state', string='State',
        compute=l_parent_compute('state_id'),
        inverse=l_parent_inverse('state_id'),
        store=True, recursive=True,
    )
    state_name = fields.Char(
        related='state_id.name', string='State Name')
    _state_id = fields.Many2one(
        'res.country.state', string='System State')
    state_id_use_parent = fields.Boolean(
        string="Use Parent State"
    )
    state_id_readonly = fields.Boolean(
        related='state_id_use_parent', readonly=True)

    country_id = fields.Many2one(
        'res.country', string='Country',
        default=_default_country_id,
        compute=l_parent_compute('country_id'),
        inverse=l_parent_inverse('country_id'),
        store=True, recursive=True,
    )
    country_name = fields.Char(
        related='country_id.name', string='Country Name')
    _country_id = fields.Many2one(
        'res.country', string='System Country')
    country_id_use_parent = fields.Boolean(
        string="Use Parent Country"
    )
    country_id_readonly = fields.Boolean(
        related='country_id_use_parent', readonly=True)

    # Geolocation
    longitude = fields.Float(digits=(16, 5))
    latitude = fields.Float(digits=(16, 5))

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         ("The title of the Location should not be the description")),
    ]

    @property
    def top_level_parent(self):
        if self.exists():
            self.ensure_one()
            location = self
            while location.parent_id:
                location = location.parent_id
            return location
        return self

    def _compute_child_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='child_ids'
        )
        for record in self:
            record.child_count = mapped_data.get(record.id, 0)

    def _compute_child_all_count(self):
        for record in self:
            record.child_all_count = len(record.child_all_ids)

    def init(self):
        # Create relation (location_id <-> parent_location_id) as PG View
        # This relation is used to compute field parent_ids
        create_sql_view(
            self.env.cr, 'generic_location_parents_rel_view',
            """
                SELECT c.id AS child_id,
                       p.id AS parent_id
                FROM generic_location AS c
                LEFT JOIN generic_location AS p ON (
                    p.id::character varying IN (
                        SELECT * FROM unnest(regexp_split_to_array(
                            c.parent_path, '/')))
                    AND p.id != c.id)
            """)

    @post_create('parent_id')
    @post_write('parent_id')
    def _post_write_invalidate_childs_cache(self, changes):
        self.invalidate_model(['parent_ids'])

    # TODO rewrite method
    # this decorator is deprecated and removed in Odoo 13
    def copy(self, default=None):
        # pylint: disable=copy-wo-api-one
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', (u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = (u"Copy of {}").format(self.name)
        else:
            new_name = (u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(GenericLocation, self).copy(default)

    def action_button_show_sublocations(self):
        action = self.get_action_by_xmlid(
            'generic_location.generic_location_action',
            context={'default_parent_id': self.id},
            domain=[('parent_id', '=', self.id)],
        )
        action.update({
            'name': _('Sublocations'),
            'display_name': _('Sublocations'),
        })
        return action

    @api.onchange('parent_id')
    def onchange_parent(self):
        for record in self:
            if record.parent_id:
                record.street_use_parent = True
                record.street2_use_parent = True
                record.zip_use_parent = True
                record.city_use_parent = True
                record.state_id_use_parent = True
                record.country_id_use_parent = True
            else:
                record.street_use_parent = False
                record.street2_use_parent = False
                record.zip_use_parent = False
                record.city_use_parent = False
                record.state_id_use_parent = False
                record.country_id_use_parent = False
