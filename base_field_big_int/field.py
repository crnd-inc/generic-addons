from odoo import fields


class BigInt(fields.Integer):
    _column_type = ('int8', 'int8')

    def convert_to_read(self, value, record, use_display_name=True):
        return value
