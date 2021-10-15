from odoo import models, fields, api


class GenericTagModelMixin(models.AbstractModel):
    _name = "generic.tag.model.mixin"
    _description = "Generic Tag Model Mixin"

    @api.model
    def _get_default_model_id(self):
        """ Try to get default model from context and find
            approriate generic.tag.model record
        """
        default_model = self.env.context.get('default_model', False)

        if default_model:
            return self.env['generic.tag.model'].search(
                [('model', '=', default_model)], limit=1)

        return self.env['generic.tag.model'].browse()

    model_id = fields.Many2one(
        "generic.tag.model", "Model", required=True, ondelete='cascade',
        default=_get_default_model_id,
        help="Specify model for which this tag is available")
