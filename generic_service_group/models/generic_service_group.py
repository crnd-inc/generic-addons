from odoo import models


class GenericServiceGroup(models.Model):
    _name = 'generic.service.group'
    _description = 'Generic Service Group'
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
    ]
