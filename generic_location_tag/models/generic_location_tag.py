from odoo import models


import logging
_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'generic.location',
        'generic.tag.mixin',
    ]
