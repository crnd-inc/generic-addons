import logging
from odoo.tests.common import tagged
from .common import GenericTeamCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestGenericTeamBase(GenericTeamCase):

    def test__get_team_users(self):
        self.assertEqual(
            self.team_1._get_team_users(),
            self.team_user_1 + self.team_user_3 + self.team_user_4)
        self.assertEqual(
            self.team_2._get_team_users(),
            (self.team_user_1 + self.team_user_2 +
             self.team_user_3 + self.team_user_4))
        self.assertEqual(
            self.team_3._get_team_users(),
            self.team_user_2 + self.team_user_4)

        self.team_3.task_manager_id = self.team_user_1
        self.assertEqual(
            self.team_3._get_team_users(),
            self.team_user_1 + self.team_user_2 + self.team_user_4)

    def test__check_user_in_team(self):
        self.assertFalse(
            self.team_1._check_user_in_team(self.env['res.users']))
        self.assertEqual(self.team_1.leader_id, self.team_user_1)
        self.assertTrue(
            self.team_1._check_user_in_team(self.team_user_1))
        self.assertNotIn(
            self.team_user_2,
            self.team_1.leader_id + self.team_1.task_manager_id +
            self.team_1.user_ids)
        self.assertFalse(
            self.team_1._check_user_in_team(self.team_user_2))

        self.team_1.task_manager_id = self.team_user_2
        self.assertTrue(
            self.team_1._check_user_in_team(self.team_user_2))
        self.team_1.task_manager_id = False
        self.assertFalse(
            self.team_1._check_user_in_team(self.team_user_2))

        self.team_1.leader_id = self.team_user_2
        self.assertTrue(
            self.team_1._check_user_in_team(self.team_user_2))

        self.team_1.leader_id = self.team_user_1
        self.assertFalse(
            self.team_1._check_user_in_team(self.team_user_2))

        self.team_1.write({
            'user_ids': [(4, self.team_user_2.id, 0)]
        })
        self.assertTrue(
            self.team_1._check_user_in_team(self.team_user_2))

    def test__team_member__name_get(self):
        self.assertGreater(len(self.team_3.team_member_ids), 0)
        team_member = self.team_3.team_member_ids[0]
        self.assertEqual(team_member.user_id, self.team_user_2)
        self.assertEqual(
            team_member.display_name,
            "%s (%s)" % (self.team_user_2.display_name,
                         self.team_3.display_name))
