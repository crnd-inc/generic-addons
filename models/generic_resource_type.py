from odoo import fields, models, api, exceptions, _


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
    show_resources_action_id = fields.Many2one(
        'ir.actions.act_window', readonly=True)
    resource_visibility = fields.Selection(
        [('internal', 'Visible only to employees'),
         ('portal', 'Visible to employees and portal users'),
         ('public', 'Visible for unregistered users')],
        default='internal', required=True)

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

    @api.constrains('model_id', 'show_resources_action_id')
    def check_show_resource_action_model(self):
        for record in self:
            if not record.show_resources_action_id:
                continue
            if record.model != record.show_resources_action_id.res_model:
                raise exceptions.ValidationError(_(
                    "Wrong 'Show Resources Action' for resource type '%s'"
                    "") % record.name)

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
    def get_resource_type(self, model_name):
        return self.search([('model_id.model', '=', model_name)], limit=1)

    @api.multi
    def get_resource_by_id(self, res_id):
        """
            Returns recordset of resource for res_id from model_id.model.

        :param res_id: int id of related record.
        :return: Recordset of resource model_id.model.
        """
        self.ensure_one()
        return self.env[self.sudo().model_id.model].browse(res_id).exists()

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

    @api.multi
    def action_show_resources(self):
        self.ensure_one()
        if self.show_resources_action_id:
            return self.show_resources_action_id.read()[0]
        return {
            'type': 'ir.actions.act_window',
            'name': self.model_id.name,
            'res_model': self.model_id.model,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
        }
