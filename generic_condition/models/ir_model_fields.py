from odoo import models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def get_field_selections(self):
        self.ensure_one()
        field_info = self.env[self.model].fields_get(
            [self.name], ['selection'])
        selection = field_info.get(self.name, {}).get('selection', [])
        return [list(s) for s in selection]
