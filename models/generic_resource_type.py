from odoo import fields, models, api, tools, exceptions, _

from odoo.tools import pycompat


class GenericResourceType(models.Model):
    _name = 'generic.resource.type'
    _description = "Generic Resource Type"
    _order = 'sequence asc, name asc, model_id asc'

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
    image_variant = fields.Binary(attachment=True)
    image = fields.Binary(compute='_compute_images',
                          inverse='_inverse_set_image')
    image_small = fields.Binary(compute='_compute_images',
                                inverse='_inverse_set_image_small')
    image_medium = fields.Binary(compute='_compute_images',
                                 inverse='_inverse_set_image_medium')

    _sql_constraints = [
        ('model_id_uniq',
         'UNIQUE (model_id)',
         'For each Odoo model only one Resource Type can be created!'),
    ]

    @api.depends('image_variant')
    def _compute_images(self):
        for record in self:
            if record._context.get('bin_size'):
                record.image_medium = record.image_variant
                record.image_small = record.image_variant
                record.image = record.image_variant
            else:
                resized_images = \
                    tools.image_get_resized_images(record.image_variant,
                                                   return_big=True,
                                                   avoid_resize_medium=True)
                record.image_medium = resized_images['image_medium']
                record.image_small = resized_images['image_small']
                record.image = resized_images['image']

    def _inverse_set_image(self):
        for record in self:
            record._set_image_value(self.image)

    def _inverse_set_image_medium(self):
        for record in self:
            record._set_image_value(self.image_medium)

    def _inverse_set_image_small(self):
        for record in self:
            record._set_image_value(self.image_small)

    def _set_image_value(self, value):
        for record in self:
            if isinstance(value, pycompat.text_type):
                value = value.encode('ascii')
            image = tools.image_resize_image_big(value)
            record.image_variant = image

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
                'src_model': self.model,
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
        res_type_ids = self._search(
            [('model_id.model', '=', model_name)], limit=1)
        return res_type_ids[0] if res_type_ids else False

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

    @api.model
    def create(self, vals):
        record = super(GenericResourceType, self).create(vals)
        self._get_resource_type_id.clear_cache(self)
        record._create_context_action_for_target_model()
        return record

    def unlink(self):
        self.mapped('resource_related_res_action_id').unlink()
        res = super(GenericResourceType, self).unlink()
        self._get_resource_type_id.clear_cache(self)
        return res

    def action_show_resources(self):
        self.ensure_one()
        if self.show_resources_action_id:
            return self.show_resources_action_id.read()[0]
        return {
            'type': 'ir.actions.act_window',
            'name': self.model_id.name,
            'res_model': self.model_id.model,
            'view_mode': 'tree,form',
            'target': 'current',
        }
