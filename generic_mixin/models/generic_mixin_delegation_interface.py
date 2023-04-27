import logging
from odoo import models, api, _
from ..tools.generic_m2o import generic_m2o_get

_logger = logging.getLogger(__name__)


def interface_proxy(fn):
    """ Make the decorated method to be available from implementation model
    """
    fn.__interface_proxy__ = True
    return fn


class GenericMixinDelegationInterface(models.AbstractModel):
    """ Mixin that have to help to deal with "inheritance via delegation".
        This is companion mixin to 'generic.mixin.delegation.mixin.

        Inheritance via delegation with multiple implementations is concept,
        when you have single interface model (that contain basic fields and
        possibly methods) and multiple implementation models for
        this interface.

        For example, we could have basic interface model
        named Resource that could have following implementations:
            - Notebook
            - Workstation
            - Car
            - Printer

        Logically, each of these models could have it's own set of fields
        that represents some characteristics. But for example for accounting
        we need only some subset of fields and methods defined by interface.
        But to make to manage this, for example assign
        some resource for some employee, we have to have different
        characteristics for each type of resource, thus we have to have
        specific model for each resource.

        Other example could be interface Device, and different implementations
        of devices

        And this mixin have to help to automatically handle one2one relation
        between interface and implementation.

        Mixin `generic.mixin.delegation.interface` is responsible for interface
        concept.
        Mixin `generic.mixin.delegation.implementation` is responsible for
        implementation of interface concept

        For example, to create new interface Thing, we have to create model
        inheriting this mixin, and define there fields that will point to
        implementation:

            class Thing(models.Model):
                _name = 'my.thing'
                _inherit = 'generic.mixin.delegation.interface'

                _generic_mixin_implementation_model_field = \
                    'implementation_model'
                _generic_mixin_implementation_id_field = 'implementation_id'

                implementation_model = fields.Char(
                    required=True, index=True, readonly=True)
                implementation_id = fields.Integer(
                    required=True, index=True, readonly=True)

                # Next define interface-specific fields:
                uuid = fields.Char()
                label = fields.Char()
                state = fields.Selection(
                    [('draft', 'Draft'),
                     ('active', 'Active')]

        Next, to be able to define implementations of this interface, we
        have to create implementation mixin, that have to inherit from
        companion mixin 'generic.mixin.delegation.implementation' and,
        this new mixin have to define delegated m2o field that points
        to Thing interface. for example:

            class ThingImplementationMixin(models.AbstractModel):
                _name = 'my.thing.implementation.mixin'
                _inherit = 'generic.mixin.delegation.implementation'

                # Here we have to define field, that points to interface model,
                # also, pay attention to 'delegate=True' paramater that is
                # required to make it work.
                thing_id = fields.Many2one(
                    'my.thing', index=True, auto_join=True,
                    required=True, delegate=True, ondelete='restrict')

        Then you can define multiple implementations of Thing using
        mixin created above.
        For example:

            class Vehicle(models.Model):
                _name = "my.vehicle"
                _inherit = 'my.thing.implementation.mixin'

                vehicle_color = fields.Char()

            class Workstation(models.Model):
                _name = 'my.workstation'
                _inherit = 'my.thing.implementation.mixin'

                workstation_cpu = fields.Char()
                workstation_memory = fields.Char()

        Next, everywhere where you need to point to anything that implements
        mentioned interface, you can use regular many2one fields that point
        to interface and work with interface. And interface itself can access
        implementation and delegate some work to implementation if needed.
        For example:

            class ThingActivationOrder(models.Model):
                _name = 'my.thing.activation.order'

                thing_id = fields.Many2one('my.thing', required=True)
                user_id = fields.Many2one('res.users')

                def action_activate_thing(self):
                    self.ensure_one()
                    self.thing_id.state = 'active'

        This way, it is possible to implement processes that do not depend on
        concrete implementation model, but require only some kind of interface.
        Also, these mixins automatically handles clean-up actions on deletion
        and automatic backlinks from interface record to implementation record
        via generic many2one (model_name + record_id) fields.
    """
    _name = 'generic.mixin.delegation.interface'
    _inherit = [
        'generic.mixin.guard.fields',
    ]
    _description = 'Generic Mixin Delegation: Interface'

    # Names of fields that have to point to name of model of implementation
    # and ID of implementation record in implementation model
    # TODO: Add validation
    _generic_mixin_implementation_model_field = None  # Required
    _generic_mixin_implementation_id_field = None  # Required

    def _generic_mixin_guard__get_guard_fields(self):
        res = super()._generic_mixin_guard__get_guard_fields() + [
            self._generic_mixin_implementation_id_field
        ]
        return res

    def name_get(self):
        result = []
        for record in self:
            implementation = generic_m2o_get(
                record,
                field_res_model=self._generic_mixin_implementation_model_field,
                field_res_id=self._generic_mixin_implementation_id_field)
            if implementation:
                result += [(record.id, implementation.display_name)]
            else:
                result == [(record.id, _("Error: unknown implementation"))]
        return result

    @api.model
    def _setup_complete(self):
        """ Setup recomputation triggers, and complete the model setup. """
        res = super()._setup_complete()

        if self._name == 'generic.mixin.delegation.interface':
            return res

        # Proxy interface methods to implementations
        for implementation_model in type(self)._inherits_children:
            if implementation_model not in self.env:
                continue
            impl = self.env[implementation_model]
            if hasattr(impl, '_setup__update_interface_proxy_methods'):
                impl._setup__update_interface_proxy_methods()

        return res
