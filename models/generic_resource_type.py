from odoo import fields, models, api


class GenericResourceType(models.Model):
    _name = 'generic.resource.type'
    _description = "Generic Resource Type"

    name = fields.Char(index=True, required=True, translate=True)
    active = fields.Boolean(index=True, default=True)
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True, index=True, auto_join=True,
        domain=[('transient', '=', False),
                ('field_id.name', '=', 'resource_id')],
        delegate=True, ondelete='cascade')
    resource_ids = fields.One2many(
        'generic.resource', 'res_type_id', string='Resources')
    resource_count = fields.Integer(compute="_compute_resource_count")

    resource_related_res_action_id = fields.Many2one(
        'ir.actions.act_window', readonly=True)

    _sql_constraints = [
        ('model_id_uniq',
         'UNIQUE (model_id)',
         'For each Odoo model only one Resource Type can be created!'),
    ]

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for rec in self:
            rec.resource_count = len(rec.resource_ids)

    @api.onchange('model_id')
    def _onchange_model_id(self):
        for rec in self:
            if rec.model_id:
                rec.name = rec.model_id.name

    def _create_context_action_for_target_model(self):
        for record in self:
            if not record.resource_related_res_action_id:
                action = self.env['ir.actions.act_window'].create({
                    'name': 'Related Resources',
                    'binding_type': 'action',
                    'binding_model_id': record.model_id.id,
                    'res_model': 'generic.resource',
                    'src_model': record.model,
                    'view_mode': 'tree,form',
                    'target': 'current',
                    'view_type': 'form',
                    'domain': (
                        "[('res_id', 'in', active_ids),"
                        "('res_model', '=', active_model)]"),
                })
                record.resource_related_res_action_id = action

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        record = super(GenericResourceType, self).create(vals)
        record._create_context_action_for_target_model()
        return record

    @api.multi
    def unlink(self):
        self.mapped('resource_related_res_action_id').unlink()
        return super(GenericResourceType, self).unlink()
