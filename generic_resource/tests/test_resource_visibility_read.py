from odoo.exceptions import AccessError
from odoo.tests.common import tagged
from .common import TestResourceVisibilityBase


@tagged('post_install', '-at_install')
class TestResourceRoleRead(TestResourceVisibilityBase):

    def test_internal_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(
            self.resource_internal.with_user(self.user).read(['name']))

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.portal_user).read(['name'])

        with self.assertRaises(AccessError):
            self.resource_internal.with_user(self.public_user).read(['name'])

    def test_portal_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(
            self.resource_portal.with_user(self.user).read(['name']))
        self.assertTrue(
            self.resource_portal.with_user(self.portal_user).read(['name']))

        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.public_user).read(['name'])

        # Remove group 'Portal' from portal user
        self.portal_user.groups_id -= self.env.ref('base.group_portal')
        self.assertFalse(self.portal_user.has_group('base.group_portal'))

        # Ensure that such user cannot read portal resources
        with self.assertRaises(AccessError):
            self.resource_portal.with_user(self.portal_user).read(['name'])

    def test_public_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(
            self.resource_public.with_user(self.user).read(['name']))
        self.assertTrue(
            self.resource_public.with_user(self.portal_user).read(['name']))

        self.assertTrue(
            self.resource_public.with_user(self.public_user).read(['name']))
