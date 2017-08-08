# -*- coding: utf-8 -*-
from openerp import models, fields


class BaseActionRule(models.Model):
    _inherit = "base.action.rule"

    pre_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_pre_condition_rel',
        string='Pre Conditions', help="Pre conditions (Generic conditions)")
    post_condition_ids = fields.Many2many(
        'generic.condition', 'base_action_rule_post_condition_rel',
        string='Post Conditions', help="Post conditions (Generic conditions)")

    # TODO: rewrite in new API
    def onchange_kind(self, cr, uid, ids,
                      kind, context=None
                     ):  # pylint: disable=old-api7-method-defined
        res = super(BaseActionRule, self).onchange_kind(
            cr, uid, ids, kind, context=context)

        if kind != 'on_write':
            res['value']['pre_condition_ids'] = [(5, 0)]

        return res

    # TODO: rewrite in new API
    def onchange_model_id(self, cr, uid, ids,
                          model_id, context=None
                         ):  # pylint: disable=old-api7-method-defined
        res = super(BaseActionRule, self).onchange_model_id(
            cr, uid, ids, model_id, context=context)

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
