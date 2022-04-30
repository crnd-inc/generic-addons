import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class GenericTeamCase(TransactionCase):

    """ Base tests case for tests related to generic team
    """

    def setUp(self):
        super(GenericTeamCase, self).setUp()
        self.team_user_1 = self.env.ref('generic_team.team_res_users_user1')
        self.team_user_2 = self.env.ref('generic_team.team_res_users_user2')
        self.team_user_3 = self.env.ref('generic_team.team_res_users_user3')
        self.team_user_4 = self.env.ref('generic_team.team_res_users_user4')

        self.team_1 = self.env.ref('generic_team.generic_team_team1')
        self.team_2 = self.env.ref('generic_team.generic_team_team2')
        self.team_3 = self.env.ref('generic_team.generic_team_team3')
