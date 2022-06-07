from odoo import models, fields, api


class GenericServiceGroup(models.Model):
    _name = 'generic.service.group'
    _description = 'Generic Service Group'
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
    ]

    active = fields.Boolean(index=True, default=True)
    service_ids = fields.One2many('generic.service', 'service_group_id')
    service_count = fields.Integer(readonly=True,
                                   compute="_compute_service_count")

    @api.depends('service_ids')
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = len(rec.service_ids)

    def action_show_service(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_service.generic_service_action',
            context=dict(
                self.env.context,
                default_service_group_id=[(4, self.id)]),
            domain=[('service_group_id.id', '=', self.id)]
        )
