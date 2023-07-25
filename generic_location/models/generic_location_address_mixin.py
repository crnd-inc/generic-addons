from odoo import models


# Obsolete, kept for backward compatibility
# TODO: Remove in 16.0
class GenericLocationAddressMixin(models.AbstractModel):
    _name = 'generic.location.address.mixin'
    _inherit = 'generic.location.mixin'
    _description = 'Generic Location Address Mixin'
