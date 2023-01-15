from odoo import models, api


class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        result = super().get_views(views, options=options)

        for model, fields_data in result.get('models', {}).items():
            many2one_reference_fields = filter(
                lambda x: x.get('type', False) == 'many2one_reference',
                fields_data.values())
            fields = self.env[model]._fields
            for field_data in many2one_reference_fields:
                field_name = field_data.get('name', False)
                if not field_name:
                    continue
                field = fields[field_name]
                model_field = field.model_field
                if model_field:
                    field_data['model_field'] = model_field

        return result
