from odoo import fields
from .field import BigInt

if not hasattr(fields, 'BigInt'):
    fields.BigInt = BigInt
