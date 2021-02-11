from odoo import models, fields

# Different type of usages of UUID mixin


class TestGenericMixinUUIDStandard(models.Model):
    _name = 'test.generic.mixin.uuid.standard'
    _inherit = [
        'generic.mixin.uuid',
    ]
    _generic_mixin_uuid_auto_add_field = True

    name = fields.Char()
