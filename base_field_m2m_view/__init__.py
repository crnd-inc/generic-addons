import odoo
from .fields import Many2manyView

if not hasattr(odoo.fields, 'Many2manyView'):
    odoo.fields.Many2manyView = Many2manyView
