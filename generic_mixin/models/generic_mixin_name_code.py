import logging
import re
import unicodedata
from odoo import api, fields, models

try:
    import slugify as slugify_lib
except ImportError:
    slugify_lib = None

_logger = logging.getLogger(__name__)


class GenericMixinNameWithCode(models.AbstractModel):
    _name = 'generic.mixin.name_with_code'
    _description = 'Generic Mixin: Name with code'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)

    _code_ascii_only = models.Constraint(
        r"CHECK (code ~ '^[a-zA-Z0-9\-_\.]*$')",
        'Code must be ascii only',
    )

    @api.model
    def _generic_mixin_name_to_code(self, name):
        """ Convert name to ascii-only code (transliterating if possible)
        """
        if slugify_lib:
            return slugify_lib.slugify(name)
        code = unicodedata.normalize('NFKD', name).encode(
            'ascii', 'ignore').decode('ascii')
        return re.sub(r'[^a-z0-9]+', '-', code.lower()).strip('-')

    @api.onchange('name', 'code')
    def _onchange_mixin_name_set_code(self):
        for record in self:
            if record.name and not record.code:
                record.code = self._generic_mixin_name_to_code(record.name)


class GenericMixinUniqNameCode(models.AbstractModel):
    _name = 'generic.mixin.uniq_name_code'
    _description = 'Generic Mixin: Unique name and code'

    _name_uniq = models.Constraint(
        "UNIQUE (name)",
        'Name must be unique.',
    )
    _code_uniq = models.Constraint(
        "UNIQUE (code)",
        'Code must be unique.',
    )
