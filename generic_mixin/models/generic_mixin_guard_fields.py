import logging
from odoo import models, api, exceptions, _

_logger = logging.getLogger(__name__)


class GenericMixinGuardFields(models.AbstractModel):
    """ This mixin is desined to be able to disable writes on some field,
        or restrict writes to some fields to be available only in specific
        places.

        In case of deny write to fields, that value for those fields will
        be silently (with only log message) removed from data
        passed to create/write methods.

        In case of guarded fields, this mixin will allow to write to that
        fields only if value was wrapped with correct wrapper.
    """
    _name = 'generic.mixin.guard.fields'
    _description = 'Generic Mixin: Guard Fields'

    _generic_mixin_guard_fields = []
    _generic_mixin_deny_write_fields = []

    class GuardInteger(int):
        """ Guard class for integer fields.
        """
        def unwrap(self):
            return int(self)

    class GuardMany2oneReference(int):
        """ Guard class for many2one_reference fields.
        """
        def unwrap(self):
            return int(self)

    def _generic_mixin_guard__get_guard_class(self, field_name):
        """ This method will return Guard class for specified field.

            :param str field_name: Name of field to get wrapper class for.
            :return class: Class that have to be used to wrap field value.
            :raises TypeError: In case if there is no wrapper for type of
                specified field.
        """
        if self._fields[field_name].type == 'integer':
            return self.GuardInteger
        if self._fields[field_name].type == 'many2one_reference':
            return self.GuardMany2oneReference
        raise TypeError(
            "Field %s could not be guarded. Type %s is not supported." % (
                field_name, self._fields[field_name].type
            ))

    def _generic_mixin_guard__wrap_field(self, field_name, value):
        """ Wrap value for specified field with correct class before
            passing it to write method.

            :param str field_name: Name of field to wrap value for.
            :param value: Value to wrap.
            :return: value wrapped with correct class
        """
        GuardClass = self._generic_mixin_guard__get_guard_class(field_name)
        return GuardClass(value)

    def _generic_mixin_guard__do_guard_fields(self, vals):
        res = dict(vals)
        for field_name in self._generic_mixin_deny_write_fields:
            if field_name in res:
                _logger.warning(
                    "Trying update / create object with '%s' "
                    "field specified, but this field will be computed "
                    "automatically.", field_name)
                del res[field_name]

        for field_name in self._generic_mixin_guard_fields:
            if field_name not in res:
                continue
            val = res[field_name]
            GuardClass = self._generic_mixin_guard__get_guard_class(field_name)
            if isinstance(val, GuardClass):
                res[field_name] = val.unwrap()
            elif val:
                raise exceptions.ValidationError(_(
                    "Direct modification of '%(model)s:%(field_name)s' "
                    "field is is not allowed!"
                ) % {
                    'model': self._name,
                    'field_name': field_name,
                })

        return res

    @api.model
    def create(self, vals):
        res = self._generic_mixin_guard__do_guard_fields(vals)
        return super().create(res)

    def write(self, vals):
        res = self._generic_mixin_guard__do_guard_fields(vals)
        return super().write(res)
