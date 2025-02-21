from odoo import models, fields, api


class BaseAutomation(models.Model):
    _inherit = "base.automation"

    pre_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_pre_condition_rel',
        string='Pre Conditions', help="Pre conditions (Generic conditions)")
    post_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_post_condition_rel',
        string='Post Conditions', help="Post conditions (Generic conditions)")

    @api.onchange('trigger')
    def _onchange_trigger(self):
        triggers = ['on_write', 'on_create_or_write']
        for record in self:
            if record.trigger not in triggers:
                record.pre_condition_ids = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for record in self:
            record.pre_condition_ids = False
            record.post_condition_ids = False

    def _filter_pre(self, records, feedback=False):
        if self.pre_condition_ids:
            records = records.filtered(self.pre_condition_ids.check)
        return super(BaseAutomation, self)._filter_pre(records, feedback)

    def _filter_post(self, records, feedback=False):
        if self.post_condition_ids:
            records = records.filtered(self.post_condition_ids.check)
        return super(BaseAutomation, self)._filter_post(records, feedback)
