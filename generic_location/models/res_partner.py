from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class ResPartner(models.Model):
    _inherit = 'res.partner'

    generic_location_ids = fields.One2many(
        comodel_name='generic.location',
        inverse_name='partner_id',
        readonly=True,
    )
    generic_location_count = fields.Integer(
        compute='_compute_generic_location_count', readonly=True)

    @api.depends()
    def _compute_generic_location_count(self):
        mapped_data = read_counts_for_o2m(
            records=self,
            field_name='generic_location_ids'
        )
        for record in self:
            record.generic_location_count = mapped_data.get(record.id, 0)

    def action_show_related_generic_locations(self):
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_location.generic_location_action',
            context={'default_partner_id': self.id},
            domain=[('partner_id', '=', self.id)],
        )
