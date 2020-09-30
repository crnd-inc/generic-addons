from odoo import models, fields, api, _


class GenericTagModel(models.Model):
    _name = "generic.tag.model"
    _inherits = {'ir.model': 'res_model_id'}
    _description = "Generic Tag Model"
    _access_log = False

    def _compute_tags_count(self):
        for model in self:
            model.tags_count = self.env['generic.tag'].search_count(
                [('model_id', '=', model.id)])

    res_model_id = fields.Many2one(
        'ir.model', 'Odoo Model', required=True, index=True, auto_join=True,
        domain=[('transient', '=', False),
                ('field_id.name', '=', 'tag_ids')],
        ondelete='cascade')

    tags_count = fields.Integer(
        string="Tags", compute="_compute_tags_count", store=False,
        readonly=True, help="How many tags related to this model exists")

    act_manage_tags_id = fields.Many2one(
        'ir.actions.act_window', readonly=True)

    _sql_constraints = [
        ('res_model_id_uniq',
         'UNIQUE (res_model_id)',
         'For each Odoo model only one Tag Model could be created!'),
    ]

    def _create_context_action_for_target_model(self):
        ActWindow = self.env['ir.actions.act_window']
        for record in self:
            if not record.act_manage_tags_id:
                self.act_manage_tags_id = ActWindow.create({
                    'name': 'Manage Tags',
                    'binding_type': 'action',
                    'binding_model_id': self.res_model_id.id,
                    'res_model': 'generic.tag.wizard.manage.tags',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': (
                        "{"
                        "'manage_tags_model': active_model,"
                        "'manage_tags_object_ids': active_ids,"
                        "}"),
                })

    @api.model
    def create(self, vals):
        record = super(GenericTagModel, self).create(vals)
        record._create_context_action_for_target_model()
        return record

    def unlink(self):
        self.mapped('act_manage_tags_id').unlink()
        return super(GenericTagModel, self).unlink()

    def action_show_tags(self):
        self.ensure_one()
        ctx = dict(self.env.context, default_model_id=self.id)
        return {
            'name': _('Tags related to model %s') % self.name,
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
        "generic.tag.model", "Model", required=True, ondelete='cascade',
        default=_get_default_model_id,
        help="Specify model for which this tag is available")
