from odoo import fields, models, api, tools, exceptions, _
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m


class GenericResourceType(models.Model):
    '''
            Creating new resource type.
    To correctly create a new resource type and bind it to the corresponding
    model, you need to perform the following steps.
    Example:
        1. In the module, in the models folder, create a model
    file your_model.py or use an already created one.
    The model must inherit the mixin ‘generic.resource.mixin’

    class YourModel(models.Model):
        _name = 'your.model'
        _inherit = 'generic.resource.mixin'

        2. In the module, in the data folder, create the file
    generic_resource_type.xml with a description of the new type
    of resource where the new model must be specified

        <?xml version="1.0" encoding="utf-8"?>
        <odoo noupdate="1">
            <record id="generic_resource_type_your_model"
                    model="generic.resource.type">
                <field name="name">Generic Resource Type Your Model</field>
                <field name="model_id" ref="model_your_model"/>
            </record>
        </odoo>

    It`s all!
    A new resource type has been created.
    '''
    _name = 'generic.resource.type'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'image.mixin',
    ]
    _description = "Generic Resource Type"
    _order = 'sequence asc, name asc, model_id asc'
    _log_access = True

    name = fields.Char(index=True, required=True, translate=True)
    active = fields.Boolean(index=True, default=True)
    model_id = fields.Many2one(
        'ir.model', required=True, index=True, auto_join=True,
        domain=[('transient', '=', False),
                ('field_id.name', '=', 'resource_id')],
        string="Resource Model",
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
    sequence = fields.Integer(default=5, index=True)

    _sql_constraints = [
        ('model_id_uniq',
         'UNIQUE (model_id)',
         'For each Odoo model only one Resource Type can be created!'),
    ]

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        mapped_data = read_counts_for_o2m(
            records=self, field_name='resource_ids', sudo=True)
        for rec in self:
            rec.resource_count = mapped_data.get(rec.id, 0)

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
                    "Wrong 'Show Resources Action' for resource type "
                    "'%(res_type)s'"
                ) % {'res_type': record.name})

    def _create_context_action_for_target_model_single(self):
        if not self.resource_related_res_action_id:
            action = self.env['ir.actions.act_window'].create({
                'name': 'Related Resources',
                'binding_type': 'action',
                'binding_model_id': self.model_id.id,
                'res_model': 'generic.resource',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': (
                    "[('res_id', 'in', active_ids),"
                    "('res_model', '=', active_model)]"),
            })
            self.resource_related_res_action_id = action

    def _create_context_action_for_target_model(self):
        for record in self:
            record._create_context_action_for_target_model_single()

    def get_resource_tracking_fields(self):
        """ Have to be overridden in another addons

            Return set of fields to track changes in
        """
        return set()

    @api.model
    @tools.ormcache('model_name')
    def _get_resource_type_id(self, model_name):
        res_type_id = self.search(
            [('model_id.model', '=', model_name)], limit=1).id
        return res_type_id

    @api.model
    def get_resource_type(self, model_name):
        """ Return instance of resource type by model name
        """
        res_type_id = self._get_resource_type_id(model_name)
        return self.browse(res_type_id) if res_type_id else self.browse()

    def get_resource_by_id(self, res_id):
        """
            Returns recordset of resource for res_id from model_id.model.

        :param res_id: int id of related record.
        :return: Recordset of resource model_id.model.
        """
        self.ensure_one()
        return self.env[self.sudo().model_id.model].browse(res_id).exists()

    def _get_resource_defaults(self):
        """ Return dict with default values for resources
        """
        self.ensure_one()
        return {
            'res_type_id': self.id,
            'resource_visibility': self.resource_visibility,
        }

    @api.model
    def create(self, vals):
        record = super(GenericResourceType, self).create(vals)
        self.env.registry.clear_cache()
        record._create_context_action_for_target_model()
        return record

    def unlink(self):
        self.mapped('resource_related_res_action_id').unlink()
        res = super(GenericResourceType, self).unlink()
        self.env.registry.clear_cache()
        return res

    def action_show_resources(self):
        self.ensure_one()
        if self.sudo().show_resources_action_id:
            return self.sudo().show_resources_action_id.read()[0]
        return {
            'type': 'ir.actions.act_window',
            'name': self.sudo().model_id.name,
            'res_model': self.sudo().model_id.model,
            'view_mode': 'tree,form',
            'target': 'current',
        }
