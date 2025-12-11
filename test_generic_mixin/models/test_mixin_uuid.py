from odoo import models, fields

# Different type of usages of UUID mixin


class TestGenericMixinUUIDStandard(models.Model):
    _name = 'test.generic.mixin.uuid.standard'
    _inherit = [
        'generic.mixin.uuid',
    ]
    _description = "Test Generic Mixin: UUID Standard"

    name = fields.Char()
    x_uuid = fields.Char(
        index=True, required=True, readonly=True,
        size=38, default='/', copy=False, string='UUID')


class TestGenericMixinUUIDNamedField(models.Model):
    _name = 'test.generic.mixin.uuid.named.field'
    _inherit = [
        'generic.mixin.uuid',
    ]
    _description = "Test Generic Mixin: UUID named field"
    _generic_mixin_uuid_field_name = 'x_myuuid'

    name = fields.Char()
    x_myuuid = fields.Char(
        index=True, required=True, readonly=True,
        size=38, default='/', copy=False, string='UUID')
