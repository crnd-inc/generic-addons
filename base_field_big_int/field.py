from odoo import fields


class BigInt(fields.Integer):
    column_type = ('int8', 'int8')
    column_cast_from = ('int4',)

    def convert_to_read(self, value, record, use_name_get=True):
        return value
