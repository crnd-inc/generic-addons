from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slugify


class GenericMixinNameWithCode(models.AbstractModel):
    _name = 'generic.mixin.name_with_code'
    _description = 'Generic Mixin: Name with code'

    name = fields.Char(required=True, index=True, translate=True)
    code = fields.Char(required=True, index=True)

    _sql_constraints = [
        ('code_ascii_only',
         r"CHECK (code ~ '^[a-zA-Z0-9\-_]*$')",
         'Code must be ascii only'),
    ]

    # TODO: maybe use display_name?
    @api.onchange('name')
    def _onchange_mixin_name_set_code(self):
        for record in self:
            record.code = slugify(record.name or '', max_length=0)


class GenericMixinUniqNameCode(models.AbstractModel):
    _name = 'generic.mixin.uniq_name_code'
    _description = 'Generic Mixin: Unique name and code'

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Name must be unique.'),
        ('code_uniq',
         'UNIQUE (code)',
         'Code must be unique.'),
    ]
