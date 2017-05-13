# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _


class BaseActionRule(models.Model):
    _inherit = 'base.action.rule'

    act_add_tag_ids = fields.Many2many('generic.tag', 'base_action_rule_add_tag_ids_rel', 'rule_id', 'tag_id',
                                            string="Add Tags", select=True,
                                            help="Specify tags to be added to object this rule is applied to")
    act_remove_tag_ids = fields.Many2many('generic.tag', 'base_action_rule_remove_tag_ids_rel', 'rule_id', 'tag_id',
                                               string="Remove Tags", select=True,
                                               help="Specify tags to be removed from object this rule is applied to")

    # Overridden to add tag related logic
    @api.multi
    def _process(self, records):
        """ process the given action on the records """
        action_done = self._context['__action_done']
        records -= action_done.setdefault(self, records.browse())
        if not records:
            return

        model = self.env[self.model_id.model]
        if self.act_add_tag_ids and model.fields_get(['tag_ids']).get('tag_ids', False):
            action_done[self] |= records
            tag_ids_val = [(4, int(t)) for t in self.act_add_tag_ids]
            records.write({'tag_ids': tag_ids_val})

        if self.act_remove_tag_ids and model.fields_get(['tag_ids']).get('tag_ids', False):
            action_done[self] |= records
            tag_ids_val = [(3, int(t)) for t in self.act_remove_tag_ids]
            records.write({'tag_ids': tag_ids_val})

        super(BaseActionRule, self)._process(records)
