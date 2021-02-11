import uuid
from odoo import models, fields, api


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
                _generic_mixin_uuid_auto_add_field = True

        After this, your model will automaticall have field 'uuid' that will
        be unique and automatically generated on creation of model.

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
                _generic_mixin_uuid_auto_add_field = True
                _generic_mixin_uuid_field_name = 'my_uuid'
    """
    _name = 'generic.mixin.uuid'
    _description = 'Generic Mixin: UUID'

    _generic_mixin_uuid_field_name = 'uuid'
    _generic_mixin_uuid_auto_add_field = False

    @api.model
    def _add_magic_fields(self):
        res = super(GenericMixinUUID, self)._add_magic_fields()

        if not self._generic_mixin_uuid_auto_add_field:
            return res

        if self._generic_mixin_uuid_field_name not in self._fields:
            self._add_field(
                self._generic_mixin_uuid_field_name,
                fields.Char(
                    index=True, required=True, readonly=True,
                    size=38, default='/', copy=False)
            )
        return res

    @api.model
    def _generic_mixin_uuid__generate_new(self):
        """ Generate new UUID that is not used in this model yet
        """
        _uuid = str(uuid.uuid4())
        while self.with_context(active_test=False).search_count(
                [(self._generic_mixin_uuid_field_name, '=', _uuid)]) > 0:
            _uuid = str(uuid.uuid4())
        return _uuid

    @api.model
    def create(self, vals):
        vals[self._generic_mixin_uuid_field_name] = (
            self._generic_mixin_uuid__generate_new())
        return super(GenericMixinUUID, self).create(vals)
