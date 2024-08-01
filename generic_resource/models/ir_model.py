from odoo import models, fields, api, exceptions, _


class IrModel(models.Model):
    _inherit = 'ir.model'

    is_generic_resource = fields.Boolean(
        default=False,
        help="Whether this model is Generic Resource.",
    )
    generic_resource_code = fields.Char()
    resource_type_ids = fields.One2many(
        'generic.resource.type', 'model_id', readonly=True,
        string="Generic Resource Types")
    resource_type_id = fields.Many2one(
        'generic.resource.type', readonly=True, store=False,
        compute='_compute_resource_type_id',
        string="Generic Resource Type")

    @api.depends('resource_type_ids')
    def _compute_resource_type_id(self):
        for record in self:
            # We have unique constraint on resource types,
            # thus we always have zero or one
            # resource type per model
            record.resource_type_id = record.resource_type_ids

    def unlink(self):
        res_model_names = set()
        for record in self:
            if record.resource_type_id:
                # Delete generic_resource related to this model. This is
                # required to delete resources because generic resource have no
                # direct (m2o) relation to record.
                self.env[record.model].sudo().with_context(
                    active_test=False).search([]).unlink()
                res_model_names.add(record.model)
                record.resource_type_id.unlink()

        res = super(IrModel, self).unlink()

        # TODO: Check if this code is required in 14.0.
        #       AttributeError: 'generic.resource' object attribute
        #                       '_inherits_children' is read-only
        # if res_model_names:
        #    self.env['generic.resource']._inherits_children -= res_model_names
        #    self.env['generic.resource.mixin']._inherit_children -= (
        #        res_model_names)

        self.pool.setup_models(self._cr)
        return res

    @api.model_create_multi
    def create(self, vals):
        records = super(IrModel, self).create(vals)
        create_res_types = [
            {'model_id': record.id,
             'name': record.name,
             'code': record.generic_resource_code}
            for record in records
            if record.is_generic_resource and record.state == "manual"
        ]
        if create_res_types:
            self.env['generic.resource.type'].sudo().create(create_res_types)
        return records

    def write(self, vals):
        if self and 'is_generic_resource' in vals:
            # Guard agains modification of base models
            if not all(rec.state == 'manual' for rec in self):
                raise exceptions.UserError(_(
                    'Only custom models can be modified.'))

            # Do not allow undo making model generic resource
            if (not vals['is_generic_resource'] and
                    any(rec.is_generic_resource for rec in self)):
                raise exceptions.UserError(_(
                    "Field 'Is Generic Resource' cannot be changed "
                    "to 'False'."))

            res = super(IrModel, self).write(vals)
            self.flush_model()
            # setup models; this reloads custom models in registry
            self.pool.setup_models(self._cr)
            # update database schema of models
            self.pool.init_models(
                self._cr,
                self.pool.descendants(self.mapped('model'), '_inherits'),
                dict(self._context, update_custom_fields=True))
            if vals['is_generic_resource']:
                for model in self:
                    if not model.resource_type_id:
                        self.env['generic.resource.type'].create({
                            'model_id': model.id,
                            'name': model.name,
                            'code': model.generic_resource_code,
                        })
        else:
            res = super(IrModel, self).write(vals)
        return res

    def _reflect_model_params(self, model):
        vals = super(IrModel, self)._reflect_model_params(model)
        vals['is_generic_resource'] = issubclass(
            type(model), self.pool['generic.resource.mixin'])
        return vals

    @api.model
    def _instanciate(self, model_data):
        model_class = super(IrModel, self)._instanciate(model_data)
        if (model_data.get('is_generic_resource') and
                model_class._name != 'generic.resource.mixin'):
            parents = model_class._inherit or []
            if isinstance(parents, str):
                parents = [parents]
            model_class._inherit = parents + ['generic.resource.mixin']
        return model_class
