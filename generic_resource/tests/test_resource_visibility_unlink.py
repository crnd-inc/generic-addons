from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from .common import TestResourceVisibilityBase


@tagged('post_install', '-at_install')
class TestResourceRoleUnlink(TestResourceVisibilityBase):

    def test_internal_resource_unlink_employee(self):
        self.assertFalse(self.user.share)

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.user).unlink()

    def test_internal_resource_unlink_portal(self):
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.portal_user).unlink()

    def test_internal_resource_unlink_public(self):
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.public_user).unlink()

    def test_internal_resource_unlink_no_portal_no_employee(self):
        # Remove group 'Portal' from portal user
        self.portal_user.groups_id -= self.env.ref('base.group_portal')
        self.assertFalse(self.portal_user.has_group('base.group_portal'))
        self.assertFalse(self.portal_user.has_group('base.group_public'))
        self.assertTrue(self.portal_user.share)

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.portal_user).unlink()

    def test_portal_resource_unlink_employee(self):
        self.assertFalse(self.user.share)

        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.user).unlink()

    def test_portal_resource_unlink_portal(self):
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))

        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.portal_user).unlink()

        # Remove group 'Portal' from portal user
        self.portal_user.groups_id -= self.env.ref('base.group_portal')
        self.assertFalse(self.portal_user.has_group('base.group_portal'))

        # Ensure that such user cannot unlink portal resources
        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.portal_user).unlink()

    def test_portal_resource_unlink_public(self):
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.public_user).unlink()

        # Remove group 'Public' from public user
        self.public_user.groups_id -= self.env.ref('base.group_public')
        self.assertFalse(self.public_user.has_group('base.group_public'))

        # Ensure that such user cannot unlink public resources
        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.public_user).unlink()

    def test_portal_resource_unlink_no_portal_no_employee(self):
        # Remove group 'Portal' from portal user
        self.portal_user.groups_id -= self.env.ref('base.group_portal')
        self.assertFalse(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.portal_user.share)

        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.portal_user).unlink()
