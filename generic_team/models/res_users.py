from odoo import fields, models
from odoo.addons.base_field_m2m_view.fields import Many2manyView


class ResUsers(models.Model):
    _inherit = 'res.users'

    generic_team_ids = Many2manyView(
        'generic.team',
        relation='generic_team_member',
        column1='user_id',
        column2='team_id',
        string='Teams',
        readonly=True,
        help='This user is member of following generic teams')
    generic_team_member_ids = fields.One2many(
        'generic.team.member', 'user_id')

    def get_team_member(self, team_id):
        self.ensure_one()
        return self.env['generic.team.member'].sudo().search([
            ('team_id', '=', team_id.id),
            ('user_id', '=', self.id),
        ])
