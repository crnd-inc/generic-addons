import logging

import uuid
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GenericMixinUUID(models.AbstractModel):
    """ Simple mixin to add UUID field to model.

        With this mixin, all records in model will have automatically
        generate UUID writen to specified field
        (that could be created automatically)

        In the basic case, it is enough to add following to your model
        to add 'uuid' field

            class MyModel(models.Model):
                _name = 'my.model'
                _inherit = 'generic.mixin.uuid'

                uuid = fields.Char(
                    index=True, required=True, readonly=True,
                    size=38, default='/', copy=False, string='UUID')

                _sql_constraints = [
                    ('uuid_uniq',
                     'UNIQUE (uuid)',
                     'UUID must be unique.'),

        After this code, you will have your uuid field automatically
        filled with unique values on record creation.

        If you add this field to existing model, then you have also provide
        migration to automatically generate new UUIDs for existing records.
        For example, we can do following in post-migrate:

            from odoo import api, SUPERUSER_ID
            def migrate(cr, installed_version):
                env = api.Environment(cr, SUPERUSER_ID, {})
                MyModel = env['my.model'].with_context(active_test=False)
                records = MyModel.search([
                    '|', ('uuid', '=', False), ('uuid', '=', '/'),
                ])
                for record in records:
                    record.uuid = record._generic_mixin_uuid__generate_new()

        Additionally, you can use custom name for field with UUID:

            class MyModelC(models.Model):
                _name = 'my.model.c'
                _inherit = 'generic.mixin.uuid'

                _generic_mixin_uuid_field_name = 'my_uuid'

                my_uuid = fields.Char(
                    index=True, required=True, readonly=True,
                    size=38, default='/', copy=False, string='UUID')

                _sql_constraints = [
                    ('my_uuid_uniq',
                     'UNIQUE (my_uuid)',
                     'My UUID must be unique.'),
    """
    _name = 'generic.mixin.uuid'
    _description = 'Generic Mixin: UUID'

    _generic_mixin_uuid_field_name = 'uuid'
    _generic_mixin_uuid_auto_add_field = False

    # TODO: Add optional validation of UUIDs

    @api.model
    def _add_magic_fields(self):
        res = super(GenericMixinUUID, self)._add_magic_fields()

        if not self._generic_mixin_uuid_auto_add_field:
            return res

        # Add uuid field if needed
        if self._generic_mixin_uuid_field_name not in self._fields:
            _logger.warning(
                "The automatic generation of UUID field is buggy and thus "
                "deprecated. Please, instead of relying on automatically "
                "generated field, add regular field like: \n"
                "uuid = fields.Char(index=True, required=True, readonly=True, "
                "size=38, default='/', copy=False, string='UUID')\n"
                "Model: %s, Field: %s",
                self._name, self._generic_mixin_uuid_field_name)
            self._add_field(
                self._generic_mixin_uuid_field_name,
                fields.Char(
                    index=True, required=True, readonly=True,
                    size=38, default='/', copy=False, automatic=True)
            )

        return res

    @api.model_create_multi
    def create(self, vals_list):
        vals_r = []
        for vals in vals_list:
            vals_uuid = vals.get(self._generic_mixin_uuid_field_name, '/')
            if not vals_uuid or vals_uuid == '/':
                # If uuid is not provided in vals, or is equal to '/', then we
                # have to generate new uuid
                v = dict(vals)   # Copy values dict, to avoid modification
                v[self._generic_mixin_uuid_field_name] = str(uuid.uuid4())
                vals_r += [v]
            else:
                vals_r += [vals]
        return super(GenericMixinUUID, self).create(vals_r)
