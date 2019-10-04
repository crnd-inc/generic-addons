from odoo import fields
from .fields import Many2manyView

if not hasattr(fields, 'Many2manyView'):
    fields.Many2manyView = Many2manyView
