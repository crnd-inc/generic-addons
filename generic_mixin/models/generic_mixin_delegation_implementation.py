import inspect
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


def interface_proxy_method_wrapper(method_name, link_field):
    """ Generate proxy method for implementation model, to call
        original method in defined in interface model

        :param str method_name: name of method in interface model to call.
        :param str link_field: name of field used to access interface record
            from implementation record to call interface method
        :return callable: wrapped method, that will call interface meth.
    """

    def method(self, *args, **kwargs):
        interface_obj = self.mapped(link_field)
        interface_method = getattr(interface_obj, method_name)
        return interface_method(*args, **kwargs)

    return method


class GenericMixinDelegationImplementation(models.AbstractModel):
    """ Mixin that have to help to deal with "inheritance via delegation".
        This is companion mixin to 'generic.mixin.delegation.interface.

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
    _name = 'generic.mixin.delegation.implementation'
    _description = 'Generic Mixin Delegation: Implementation'
    _inherit = [
        'generic.mixin.guard.fields',
    ]

    def _generic_mixin_guard__get_deny_write_fields(self):
        res = super()._generic_mixin_guard__get_deny_write_fields() + list(
            self._generic_mixin_delegation__get_interfaces_info())
        return res

    def _generic_mixin_delegation__get_interfaces_info(self):
        """ Return dictionary with supported interfaces mapping:
                interface_field -> interface_model
        """
        # TODO: Memoize result
        return {
            field_name: m_name
            for m_name, field_name in self._inherits.items()
            if all([
                getattr(self.env[m_name],
                        '_generic_mixin_implementation_id_field', None),
                getattr(self.env[m_name],
                        '_generic_mixin_implementation_model_field', None)
            ])
        }

    @api.model
    def _add_missing_default_values(self, values):
        res = super()._add_missing_default_values(values)

        to_update = {}
        interface_info = self._generic_mixin_delegation__get_interfaces_info()
        for interface_model in interface_info.values():
            # Find delegation interface model
            Interface = self.env[interface_model]

            if Interface._generic_mixin_implementation_model_field in res:
                # If value for model field already computed then skip
                continue

            impl_model_field = Interface._fields[
                Interface._generic_mixin_implementation_model_field
            ]
            if not impl_model_field.store:
                continue
            if impl_model_field.compute:
                continue
            if impl_model_field.related:
                continue

            # Here we have to add name of implementation model on interface
            # record. Later, implementation record ID will be added
            # (when implementation will be created)
            to_update[Interface._generic_mixin_implementation_model_field] = (
                self._name)

        if to_update:
            # We have to avoid modification of input params, thus we copy res
            res = dict(res)
            res.update(to_update)
        return res

    @api.model_create_multi
    def create(self, vals):
        interface_info = self._generic_mixin_delegation__get_interfaces_info()
        values = []
        tmp_id = -1
        for vals_row in vals:
            # Copy original item from vals, to avoid side effects
            val = dict(vals_row)
            for interface_field, interface_model in interface_info.items():
                # Find delegation interface model
                Interface = self.env[interface_model]

                # Find name of field that represents ID of implementation
                implementation_id_field = (
                    Interface._generic_mixin_implementation_id_field)

                # Add fake implementation id to values.
                # This is required to create 'interface' record,
                # because 'implementation_id' field is required
                # This field will be updated after record creation completed
                val[
                    implementation_id_field
                ] = Interface._generic_mixin_guard__wrap_field(
                    implementation_id_field, tmp_id)

                # Decrement temporary ID to avoid uniq constraint violation
                tmp_id -= 1

            values += [val]

        # Create record
        records = super().create(values)

        for interface_field, interface_model in interface_info.items():
            # Find delegation interface model
            Interface = self.env[interface_model]

            # Find name of field that represents ID of implementation
            implementation_id_field = (
                Interface._generic_mixin_implementation_id_field)

            for record in records:
                # Update res_id with created id
                record.sudo()[interface_field].write({
                    implementation_id_field:
                        Interface._generic_mixin_guard__wrap_field(
                            implementation_id_field, record.id),
                })

        return records

    def unlink(self):
        interface_info = self._generic_mixin_delegation__get_interfaces_info()

        # Find delegation interfaces to be removed
        to_cleanup = {
            interface_model: self.sudo().mapped(interface_field)
            for interface_field, interface_model in interface_info.items()
        }

        # Delete records
        res = super().unlink()

        # Delete delegation interfaces and return status
        for interface_records in to_cleanup.values():
            interface_records.unlink()
        return res

    def _setup__update_interface_proxy_methods(self):
        implementation_cls = type(self)
        interface_info = self._generic_mixin_delegation__get_interfaces_info()
        for interface_field, interface_model in interface_info.items():
            # Find all proxy methods, and proxy them to implementation model
            for method_name, method in inspect.getmembers(
                    type(self.env[interface_model]), inspect.isfunction):

                if not getattr(method, '__interface_proxy__', False):
                    # If the method is not interface-proxy, then skip it
                    continue

                if hasattr(implementation_cls, method_name):
                    # We do not want to do anything if corresponding method
                    # already exists on implementation model
                    continue

                # Prepare the proxy method to be added to implementation model
                proxy_method = interface_proxy_method_wrapper(
                    method_name, interface_field)

                # Update proxy method attributes
                proxy_method.__name__ = method.__name__
                proxy_method.__doc__ = method.__doc__

                # Define method on implementation model
                setattr(implementation_cls, method_name, proxy_method)

    @api.model
    def _setup_complete(self):
        """ Setup recomputation triggers, and complete the model setup. """
        res = super()._setup_complete()

        if self._name == 'generic.mixin.delegation.implementation':
            return res

        self._setup__update_interface_proxy_methods()

        return res
