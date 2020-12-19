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
        related='leader_id.image_small', readonly=True,
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
