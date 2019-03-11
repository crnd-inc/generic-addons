from .fields import Many2manyView
from odoo import fields

if not hasattr(fields, 'Many2manyView'):
    fields.Many2manyView = Many2manyView
