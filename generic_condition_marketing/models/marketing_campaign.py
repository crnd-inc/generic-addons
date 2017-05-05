# -*- coding: utf-8 -*-
from openerp import models, fields, api


class MarketingCampaignActivity(models.Model):
    _inherit = "marketing.campaign.activity"

    condition_ids = fields.Many2many(
        'generic.condition', string='Conditions',
        help="Specify generic conditions to decide whether the activity "
             "can be executed. This is similar to 'Condition field' but uses "
             "Generic Conditions instead. These conditions are checked before "
             "'Condition' field is checked. In most cases, if you plan to "
             "use 'Generic Conditions' here, set 'Condition' field to 'True'")


class MarketingCampaignWorkitem(models.Model):
    _inherit = "marketing.campaign.workitem"

    @api.model
    def _process_one(self, workitem):
        if workitem.state != 'todo':
            return False

        activity = workitem.activity_id
        Model = self.env[workitem.object_id.model]
        obj = Model.browse(workitem.res_id)

        # If this activity uses generic conditions check them,
        # and if check fails, then unlink workitem or make it canceled!
        if activity.condition_ids and not activity.condition_ids.check(obj):
            if activity.keep_if_condition_not_met:
                workitem.write({'state': 'cancelled'})
            else:
                workitem.unlink()
            return

        return super(MarketingCampaignWorkitem, self)._process_one(workitem)
