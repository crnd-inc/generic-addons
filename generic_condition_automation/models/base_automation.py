from openerp import models, fields


class BaseAutomation(models.Model):
    _inherit = "base.automation"

    pre_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_pre_condition_rel',
        string='Pre Conditions', help="Pre conditions (Generic conditions)")
    post_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_post_condition_rel',
        string='Post Conditions', help="Post conditions (Generic conditions)")

    def onchange_kind(self):
        if self.kind != 'on_write':
            self.pre_condition_ids = False
        return super(BaseAutomation, self).onchange_kind()

    def onchange_model_id(self):
        self.pre_condition_ids = False
        self.post_condition_ids = False
        return super(BaseAutomation, self).onchange_model_id()

    def _filter_pre(self, records):
        if self.pre_condition_ids:
            records = records.filtered(self.pre_condition_ids.check)
        return super(BaseAutomation, self)._filter_pre(records)

    def _filter_post(self, records):
        if self.post_condition_ids:
            records = records.filtered(self.post_condition_ids.check)
        return super(BaseAutomation, self)._filter_post(records)
