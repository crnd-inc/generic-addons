from odoo import models, fields


class GenericTeamMember(models.Model):
    _name = 'generic.team.member'
    _description = 'Generic team member'

    user_id = fields.Many2one('res.users', index=True, required=True)
    team_id = fields.Many2one('generic.team', index=True, required=True)

    _sql_constraints = [
        ('user_team_unique',
         'UNIQUE (user_id, team_id)',
         'User may be added to team only once.'),
    ]

    def name_get(self):
        res = []
        for record in self:
            res += [(
                record.id,
                "%s (%s)" % (record.user_id.display_name,
                             record.team_id.display_name),
            )]
        return res
