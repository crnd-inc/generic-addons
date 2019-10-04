import odoo
from .field import BigInt

if not hasattr(odoo.fields, 'BigInt'):
    odoo.fields.BigInt = BigInt
