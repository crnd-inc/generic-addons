from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class GenericLocationType(models.Model):
    _name = 'generic.location.type'
    _order = 'name ASC, code ASC, id ASC'

    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
    ]
    _description = 'Location Type'

    name = fields.Char(copy=False)
    code = fields.Char(copy=False)
    active = fields.Boolean(default=True, index=True)

    # Locations
    location_ids = fields.One2many(
        'generic.location', 'type_id', 'Locations', readonly=True, copy=False)
    location_count = fields.Integer(
        'All Locations', compute='_compute_location_count', readonly=True)

    @api.depends('location_ids')
    def _compute_location_count(self):
        mapped_data = read_counts_for_o2m(
            records=self, field_name='location_ids', sudo=True)
        for rec in self:
            rec.location_count = mapped_data.get(rec.id, 0)

    def action_location_type_show_locations(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_location.generic_location_action',
            domain=[('type_id', '=', self.id)],
            context={'default_type_id': self.id})
