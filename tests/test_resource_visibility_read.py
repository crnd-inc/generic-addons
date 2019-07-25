from odoo.exceptions import AccessError
from odoo.tests.common import post_install, at_install
from .common import TestResourceVisibilityBase


@post_install(True)
@at_install(False)
class TestResourceRoleRead(TestResourceVisibilityBase):

    def test_internal_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(self.resource_internal.sudo(self.user).read())

        with self.assertRaises(AccessError):
            self.resource_internal.sudo(self.portal_user).read(['name'])

        with self.assertRaises(AccessError):
            self.resource_internal.sudo(self.public_user).read(['name'])

    def test_portal_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(self.resource_portal.sudo(self.user).read())
        self.assertTrue(
            self.resource_portal.sudo(self.portal_user).read(['name']))

        with self.assertRaises(AccessError):
            self.resource_portal.sudo(self.public_user).read(['name'])

        # Remove group 'Portal' from portal user
        self.portal_user.groups_id -= self.env.ref('base.group_portal')
        self.assertFalse(self.portal_user.has_group('base.group_portal'))

        # Ensure that such user cannot read portal resources
        with self.assertRaises(AccessError):
            self.resource_portal.sudo(self.portal_user).read(['name'])

    def test_public_resource_read(self):
        self.assertFalse(self.user.share)
        self.assertTrue(self.portal_user.share)
        self.assertTrue(self.portal_user.has_group('base.group_portal'))
        self.assertTrue(self.public_user.share)
        self.assertTrue(self.public_user.has_group('base.group_public'))

        self.assertTrue(self.resource_public.sudo(self.user).read())
        self.assertTrue(
            self.resource_public.sudo(self.portal_user).read(['name']))

        self.assertTrue(
            self.resource_public.sudo(self.public_user).read(['name']))
