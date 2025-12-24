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

    _generic_mixin_uuid_field_name = 'x_uuid'
    _generic_mixin_uuid_auto_add_field = False

    # TODO: Add optional validation of UUIDs

    @api.model
    def _post_model_setup__(self):
        super()._post_model_setup__()

        if not getattr(self, '_generic_mixin_uuid_auto_add_field', False):
            return

        field_name = getattr(self, '_generic_mixin_uuid_field_name', 'x_uuid')
        if not field_name.startswith('x_'):
            _logger.warning(
                "Automatic UUID field generation is only supported "
                "for custom fields starting with 'x_'. "
                "Please declare the field explicitly in the model. "
                "Model: %s, Field: %s",
                getattr(self, '_name', self.__class__.__name__),
                field_name,
            )
            return

        if field_name in self._fields:
            return

        try:
            from odoo.orm import model_classes
            field = fields.Char(
                index=True,
                required=True,
                readonly=True,
                size=38,
                default='/',
                copy=False,
                automatic=True,
            )
            model_classes.add_field(self.__class__, field_name, field)
            field.prepare_setup()
            field.setup(self)
        except Exception:
            _logger.exception(
                "Failed to auto-add UUID field on model during post-setup. "
                "Model: %s, Field: %s",
                getattr(self, '_name', self.__class__.__name__),
                field_name,
            )

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

    def get_by_uuid(self, u):
        """ Get record by UUID, even if it is archived

            :param str u: UUID to search record by
            :return: Recordset with record found or empty recordset.
        """
        return self.with_context(active_test=False).search([
            (self._generic_mixin_uuid_field_name, '=', u),
        ])

    def create_or_update_by_uuid(self, u, data):
        """ Create or update record by UUID.

            Useful for integration purposes.

            :param str u: UUID of record to create or update
            :param dict data: Data to write to record or to updated record with
            :return: record updated or created record
        """
        record = self.get_by_uuid(u)
        if record:
            record.write(data)
        else:
            data = dict(data)
            data[self._generic_mixin_uuid_field_name] = u
            record = self.create(data)

        return record
