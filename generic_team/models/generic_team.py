from odoo import models, fields
from odoo.addons.base_field_m2m_view.fields import Many2manyView


class GenericTeam(models.Model):
    _name = 'generic.team'
    _inherit = [
        'mail.thread',
        'generic.mixin.get.action',
    ]
    _description = 'Generic Team'

    name = fields.Char(
        index=True, required=True, translate=True,
        string='Team name')
    description = fields.Text(translate=True)
    active = fields.Boolean(index=True, default=True, string='Active?')
    leader_id = fields.Many2one(
        'res.users', required=True, index=True, string='Team leader')
    leader_name = fields.Char(  # pylint: disable=attribute-string-redundant
        related='leader_id.display_name', readonly=True,
        string="Leader Name")
    leader_image = fields.Binary(  # pylint: disable=attribute-string-redundant
        related='leader_id.image_128', readonly=True,
        string="Leader Image")
    task_manager_id = fields.Many2one(
        'res.users', index=True, string='Task manager')
    team_member_ids = fields.One2many(
        'generic.team.member', 'team_id', 'Team Members')

    # Kept for backward compatability reason
    user_ids = Many2manyView(
        'res.users',
        relation='generic_team_member',
        column1='team_id',
        column2='user_id',
        string='Team members (Users)')
    user_count = fields.Integer(
        compute='_compute_user_count', readonly=True, string='Users count')

    def _compute_user_count(self):
        for record in self:
            record.user_count = len(record.user_ids)

    def _get_team_users(self):
        self.ensure_one()
        team_users = self.user_ids.ids
        if self.leader_id and self.leader_id.id not in team_users:
            team_users += self.leader_id.ids
        if self.task_manager_id and self.task_manager_id.id not in team_users:
            team_users += self.task_manager_id.ids

        return self.env['res.users'].browse(team_users)

    def _check_user_in_team(self, user_id):
        self.ensure_one()
        if not user_id:
            return False
        return any([
            self in user_id.generic_team_ids,
            self.sudo().leader_id == user_id,
            self.sudo().task_manager_id == user_id,
        ])
