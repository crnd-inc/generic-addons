from .field import BigInt
from odoo import fields

if not hasattr(fields, 'BigInt'):
    fields.BigInt = BigInt
