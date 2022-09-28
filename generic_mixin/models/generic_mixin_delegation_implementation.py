import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


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
    """
    _name = 'generic.mixin.delegation.implementation'
    _description = 'Generic Mixin Delegation: Implementation'
    _inherit = [
        'generic.mixin.guard.fields',
    ]

    # Name of m2o field that points to delegation interface
    _generic_mixin_delegation_interface_field = None

    def _generic_mixin_guard__get_deny_write_fields(self):
        return super()._generic_mixin_guard__get_deny_write_fields() + [
            self._generic_mixin_delegation_interface_field,
        ]

    def _generic_mixin_delegation__get_interface_model(self):
        """ Return delegation interface model for this delegation mixin
        """
        return self.env[
            self._fields[
                self._generic_mixin_delegation_interface_field
            ].comodel_name
        ]

    @api.model
    def create(self, vals):
        values = dict(vals)

        # Find delegation interface model
        Interface = self._generic_mixin_delegation__get_interface_model()

        # Find name of field that represents ID of implementation
        implementation_id_field = (
            Interface._generic_mixin_implementation_id_field)

        # Add fake resource id to values. This is required to create
        # 'generic.resource' record, because 'res_id' field is required
        # This field will be updated after record creation
        values[
            implementation_id_field
        ] = Interface._generic_mixin_guard__wrap_field(
            implementation_id_field, -1)

        # Create record
        rec = super().create(values)

        # Update res_id with created id
        rec.sudo()[
            self._generic_mixin_delegation_interface_field
        ].write({
            implementation_id_field:
                Interface._generic_mixin_guard__wrap_field(
                    implementation_id_field, rec.id),
        })
        return rec

    def unlink(self):
        # Find deletagion interfaces to be removed
        delegation_interfaces = self.sudo().mapped(
            self._generic_mixin_delegation_interface_field)

        # Delete records
        res = super().unlink()

        # Delete delegation interfaces and return status
        delegation_interfaces.unlink()
        return res
