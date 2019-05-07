from odoo import models, fields, api, _


class GenericTagModel(models.Model):
    _name = "generic.tag.model"
    _inherits = {'ir.model': 'res_model_id'}
    _description = "Generic Tag Model"
    _access_log = False

    @api.multi
    def _compute_tags_count(self):
        for model in self:
            model.tags_count = self.env['generic.tag'].search_count(
                [('model_id', '=', model.id)])

    res_model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        domain=[('transient', '=', False),
                ('field_id.name', '=', 'tag_ids')],
        ondelete='restrict')

    tags_count = fields.Integer(
        string="Tags", compute="_compute_tags_count", store=False,
        readonly=True, help="How many tags related to this model exists")

    _sql_constraints = [
        ('res_model_id_uniq',
         'UNIQUE (res_model_id)',
         'For each Odoo model only one Tag Model could be created!'),
    ]

    @api.multi
    def action_show_tags(self):
        self.ensure_one()
        ctx = dict(self.env.context, default_model_id=self.id)
        return {
            'name': _('Tags related to model %s') % self.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'generic.tag',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('model_id.id', '=', self.id)],
        }


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
        "generic.tag.model", "Model", required=True, ondelete='restrict',
        default=_get_default_model_id,
        help="Specify model for which this tag is available")
