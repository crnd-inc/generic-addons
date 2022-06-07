from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m



class GenericServiceGroup(models.Model):
    _name = 'generic.service.group'
    _description = 'Generic Service Group'
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
    ]

    active = fields.Boolean(index=True, default=True)
    service_ids = fields.One2many('generic.service', 'name')
    service_count = fields.Integer(compute='_compute_service_count')
    show_service_action_id = fields.Many2one(
        'ir.actions.act_window', readonly=True)

    @api.depends('service_ids')
    def _compute_service_count(self):
        mapped_data = read_counts_for_o2m(
            records=self, field_name='service_ids', sudo=True)
        for rec in self:
            rec.service_count = mapped_data.get(rec.id, 0)

    def action_show_service(self):
        self.ensure_one()
        if self.sudo().show_service_action_id:
            return self.sudo().show_service_action_id.read()[0]
