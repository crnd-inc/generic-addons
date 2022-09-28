import logging
from odoo import models, _
from ..tools.generic_m2o import generic_m2o_get

_logger = logging.getLogger(__name__)


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
    """
    _name = 'generic.mixin.delegation.interface'
    _inherit = [
        'generic.mixin.guard.fields',
    ]
    _description = 'Generic Mixin Delegation: Interface'

    # Names of fields that have to point to name of model of implementation
    # and ID of implementation record in implementation model
    _generic_mixin_implementation_model_field = None
    _generic_mixin_implementation_id_field = None

    def _generic_mixin_guard__get_guard_fields(self):
        return super()._generic_mixin_guard__get_guard_fields() + [
            self._generic_mixin_implementation_id_field
        ]

    def name_get(self):
        result = []
        for record in self:
            implementation = generic_m2o_get(
                self,
                field_res_model=self._generic_mixin_implementation_model_field,
                field_res_id=self._generic_mixin_implementation_id_field)
            if implementation:
                result += [(record.id, implementation.display_name)]
            else:
                result == [(record.id, _("Error: unknown implementation"))]
        return result
