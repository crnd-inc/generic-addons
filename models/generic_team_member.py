from odoo import models, fields


class GenericTeamMember(models.Model):
    _name = 'generic.team.member'

    user_id = fields.Many2one('res.users', index=True, required=True)
    team_id = fields.Many2one('generic.team', index=True, required=True)
