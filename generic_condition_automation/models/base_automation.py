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

    def _filter_pre(self, records, *args, **kwargs):
        # Access the condition fields in sudo to avoid an
        # AccessError on 'base.automation' for regular users.
        self_sudo = self.sudo()
        if self_sudo.pre_condition_ids:
            # Generic conditions are readable by any user,
            # thus switch back to user env after reading them from automation
            # rule
            records = records.filtered(
                self_sudo.pre_condition_ids.with_env(self.env).check)
        return super(BaseAutomation, self)._filter_pre(
            records, *args, **kwargs)

    def _filter_post(self, records, *args, **kwargs):
        self_sudo = self.sudo()
        if self_sudo.post_condition_ids:
            # Generic conditions are readable by any user,
            # thus switch back to user env after reading them from automation
            # rule
            records = records.filtered(
                self_sudo.post_condition_ids.with_env(self.env).check)
        return super(BaseAutomation, self)._filter_post(
            records, *args, **kwargs)
