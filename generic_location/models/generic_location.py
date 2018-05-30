from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'mail.thread',
        'generic.mixin.parent.names',
    ]
    _parent_name = 'parent_id'
    _description = 'Location'

    name = fields.Char(required=True, index=True)
    description = fields.Text()
    parent_id = fields.Many2one(
        'generic.location', index=True, string='Parent Location')
    active = fields.Boolean(default=True, index=True)
    child_ids = fields.One2many(
        'generic.location', 'parent_id', string='Sublocations', readonly=True)
    child_count = fields.Integer(compute='_compute_child_count', readonly=True)

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         ("The title of the Location should not be the description")),
    ]

    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', (u"Copy of {}%").format(self.name))])
        if not copied_count:
            new_name = (u"Copy of {}").format(self.name)
        else:
            new_name = (u"Copy of {} ({})").format(self.name, copied_count)

        default['name'] = new_name
        return super(GenericLocation, self).copy(default)

    @api.multi
    def action_button_show_sublocations(self):
        return {
            'name': self.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
        }
