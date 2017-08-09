# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BaseActionRule(models.Model):
    _inherit = "base.action.rule"

    pre_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_pre_condition_rel',
        string='Pre Conditions', help="Pre conditions (Generic conditions)")
    post_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_post_condition_rel',
        string='Post Conditions', help="Post conditions (Generic conditions)")

    @api.multi
    def onchange_kind(self, kind):
        res = super(BaseActionRule, self).onchange_kind(kind)

        if kind != 'on_write':
            res['value']['pre_condition_ids'] = [(5, 0)]

        return res

    @api.multi
    def onchange_model_id(self, model_id):
        res = super(BaseActionRule, self).onchange_model_id(model_id)

        res['value']['pre_condition_ids'] = [(5, 0)]
        res['value']['post_condition_ids'] = [(5, 0)]

        return res

    def _filter_pre(self, records):
        if self.pre_condition_ids:
            records = records.filtered(self.pre_condition_ids.check)
        return super(BaseActionRule, self)._filter_pre(records)

    def _filter_post(self, records):
        if self.post_condition_ids:
            records = records.filtered(self.post_condition_ids.check)
        return super(BaseActionRule, self)._filter_post(records)
