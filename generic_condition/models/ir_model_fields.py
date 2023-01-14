from odoo import models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def get_field_selections(self):
        self.ensure_one()
        selections = self.selection_ids.read(['value', 'name'])
        return list(map(lambda x: [x['value'], x['name']], selections))
