from odoo import models, fields, api


class GenericTeam(models.Model):
    _name = 'generic.team'
    _inherit = 'mail.thread'

    name = fields.Char(index=True, required=True, translate=True,
                       string='Team name')
    description = fields.Text(translate=True)
    active = fields.Boolean(index=True, default=True, string='Active?')
    leader_id = fields.Many2one('res.users', required=True, index=True,
                                string='Team leader')
    user_ids = fields.Many2many('res.users', string='Team members')
    user_count = fields.Integer(compute='_compute_user_count',
                                readonly=True, string='Users count')

    @api.multi
    def _compute_user_count(self):
        for record in self:
            record.user_count = len(record.user_ids)
