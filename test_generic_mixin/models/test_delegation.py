from odoo import models, fields
from odoo.addons.generic_mixin import interface_proxy


class Interface1(models.Model):
    _name = "test.generic.mixin.interface.1"
    _inherit = [
        'generic.mixin.delegation.interface',

    ]
    _description = 'Test Generic Mixin: Interface 1'
    _log_access = False

    _generic_mixin_implementation_model_field = 'interface_1_impl_model'
    _generic_mixin_implementation_id_field = 'interface_1_impl_id'

    interface_1_impl_model = fields.Char(required=True)
    interface_1_impl_id = fields.Integer(required=True)

    interface_1_test_field_1 = fields.Char()

    _sql_constraints = [
        ('unique_model', 'UNIQUE(interface_1_impl_model, interface_1_impl_id)',
         'Model instance must be unique')
    ]

    @interface_proxy
    def interface_1_method_1(self, my_param):
        self.interface_1_test_field_1 = (
            "interface_1_method_1 called with param %s" % my_param)


class Interface2(models.Model):
    _name = "test.generic.mixin.interface.2"
    _inherit = [
        'generic.mixin.delegation.interface',
    ]
    _description = 'Test Generic Mixin: Interface 2'
    _log_access = False

    _generic_mixin_implementation_model_field = 'interface_2_impl_model'
    _generic_mixin_implementation_id_field = 'interface_2_impl_id'

    interface_2_impl_model = fields.Char(required=True)
    interface_2_impl_id = fields.Integer(required=True)

    interface_2_test_field_1 = fields.Char()

    _sql_constraints = [
        ('unique_model', 'UNIQUE(interface_2_impl_model, interface_2_impl_id)',
         'Model instance must be unique')
    ]

    @interface_proxy
    def interface_2_method_1(self, my_param):
        self.interface_2_test_field_1 = (
            "interface_2_method_1 called with param %s" % my_param)

    def interface_2_method_2(self):
        self.interface_2_test_field_1 = "interface_2_method_2 called!"


class ImplementationMixin1(models.AbstractModel):
    _name = 'test.generic.mixin.interface.1.impl.mixin'
    _description = 'Test Generic Mixin: Interface 1 Implementation Mixin'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.delegation.implementation',
    ]

    interface_1_id = fields.Many2one(
        'test.generic.mixin.interface.1', index=True, auto_join=True,
        required=True, delegate=True, ondelete='restrict')

    _sql_constraints = [
        ('unique_interface_1_id', 'UNIQUE(interface_1_id)',
         'Interface must be unique')
    ]


class ImplementationMixin2(models.AbstractModel):
    _name = 'test.generic.mixin.interface.2.impl.mixin'
    _description = 'Test Generic Mixin: Interface 2 Implementation Mixin'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.delegation.implementation',
    ]

    interface_2_id = fields.Many2one(
        'test.generic.mixin.interface.2', index=True, auto_join=True,
        required=True, delegate=True, ondelete='restrict')

    _sql_constraints = [
        ('unique_interface_2_id', 'UNIQUE(interface_2_id)',
         'Interface must be unique')
    ]


class TestDelegationMultiInterface(models.Model):
    _name = 'test.generic.mixin.multi.interface.impl'
    _inherit = [
        'test.generic.mixin.interface.1.impl.mixin',
        'test.generic.mixin.interface.2.impl.mixin',
        'generic.mixin.track.changes',
    ]

    name = fields.Char()


class TestDelegationModelNoDeletgation(models.Model):
    _name = 'test.gm.delegation.no.delegation'
    _description = 'Test Generic Mixin Delegation no Delegation'

    some_field = fields.Text()


class TestDelegationMultiInterfaceNoDelImpl(models.Model):
    _name = 'test.gm.multi.interface.no.del.impl'
    _inherit = [
        'test.generic.mixin.interface.1.impl.mixin',
        'generic.mixin.track.changes',
    ]

    name = fields.Char()

    test_delegate_id = fields.Many2one(
        'test.gm.delegation.no.delegation', required=True, delegate=True,
        ondelete='cascade')
