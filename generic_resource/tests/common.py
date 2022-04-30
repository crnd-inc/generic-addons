from odoo.tests.common import TransactionCase
from odoo.addons.generic_mixin.tests.common import (
    ReduceLoggingMixin
)


class TestResourceVisibilityBase(ReduceLoggingMixin, TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestResourceVisibilityBase, cls).setUpClass()

        # User
        cls.user = cls.env.ref('base.user_demo')
        cls.portal_user = cls.env.ref('base.demo_user0')
        cls.public_user = cls.env.ref('base.public_user')

        # Groups
        cls.group_resource_user = cls.env.ref(
            'generic_resource.group_generic_resource_user')
        cls.group_resource_manager = cls.env.ref(
            'generic_resource.group_generic_resource_manager')

        # Test resources
        cls.resource_internal = cls.env.ref(
            'generic_resource.simple_resource_notebook_5')
        cls.resource_portal = cls.env.ref(
            'generic_resource.simple_resource_notebook_7')
        cls.resource_public = cls.env.ref(
            'generic_resource.simple_resource_inkprinter_6')
        cls.uresource_internal = cls.resource_internal.with_user(cls.user)

        cls.resource_type = cls.env.ref(
            'generic_resource.generic_resource_type_default')
