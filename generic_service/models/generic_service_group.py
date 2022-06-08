from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class GenericServiceGroup(models.Model):
    _name = 'generic.service.group'
    _description = 'Generic Service Group'
    _order = 'sequence ASC, name ASC, id'
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
    ]

    active = fields.Boolean(index=True, default=True)
    service_ids = fields.One2many('generic.service', 'service_group_id')
    service_count = fields.Integer(
        readonly=True,
        compute="_compute_service_count")
    sequence = fields.Integer(default=5, index=True)

    @api.depends('service_ids')
    def _compute_service_count(self):
        mapped_data = read_counts_for_o2m(
            records=self, field_name='service_ids', sudo=True)
        for rec in self:
            rec.service_count = mapped_data.get(rec.id, 0)

    def action_show_service(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_service.generic_service_action',
            context=dict(
                self.env.context,
                default_service_group_id=self.id),
            domain=[('service_group_id.id', '=', self.id)]
        )
