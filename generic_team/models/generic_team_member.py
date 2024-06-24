from odoo import models, fields, api


class GenericTeamMember(models.Model):
    _name = 'generic.team.member'
    _description = 'Generic team member'

    user_id = fields.Many2one(
        'res.users', index=True, required=True, ondelete='cascade')
    team_id = fields.Many2one(
        'generic.team', index=True, required=True, ondelete='cascade')

    _sql_constraints = [
        ('user_team_unique',
         'UNIQUE (user_id, team_id)',
         'User may be added to team only once.'),
    ]

    @api.depends('user_id', 'team_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s (%s)" % (
                record.user_id.display_name, record.team_id.display_name)
