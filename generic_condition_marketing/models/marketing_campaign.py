from openerp import models, fields, api


class MarketingCampaignActivity(models.Model):
    _inherit = "marketing.campaign.activity"

    condition_ids = fields.Many2many(
        'generic.condition', string='Conditions',
        help="Specify generic conditions to decide whether the activity "
             "can be executed. This is similar to 'Condition' field but uses "
             "Generic Conditions instead. These conditions are checked before "
             "'Condition' field is checked. In most cases, if you plan to "
             "use 'Generic Conditions' here, set 'Condition' field to 'True'")


class MarketingCampaignWorkitem(models.Model):
    _inherit = "marketing.campaign.workitem"

    @api.multi
    def _process_one(self):
        if self.state != 'todo':
            return False

        activity = self.activity_id
        obj = self.env[self.object_id.model].browse(self.res_id)

        # If this activity uses generic conditions check them,
        # and if check fails, then unlink workitem or make it canceled!
        if activity.condition_ids and not activity.condition_ids.check(obj):
            if activity.keep_if_condition_not_met:
                self.write({'state': 'cancelled'})
            else:
                self.unlink()
            return

        return super(MarketingCampaignWorkitem, self)._process_one()
