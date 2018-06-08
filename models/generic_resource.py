from openerp import fields, models, api, exceptions, _


import logging
_logger = logging.getLogger(__name__)


class GenericResourceResID(int):
    """ Simple class to ensure that 'generic.resource' being created
        from 'generic.resource.mixin' code
    """
    pass


class GenericResource(models.Model):
    _name = 'generic.resource'
    _description = 'Generic Resource'
    _log_access = False

    active = fields.Boolean(default=True, index=True)
    implementation_ids = fields.One2many(
        'generic.resource.implementation', 'resource_id',
        string="Implementations")
    implementation_count = fields.Integer(
        compute="_compute_implementation_count")
    res_type_id = fields.Many2one(
        'generic.resource.type', string="Type", required=True, index=True,
        ondelete='restrict')
    res_model = fields.Char(
        related='res_type_id.model_id.model', readonly=True, store=True,
        compute_sudo=True, index=True)
    res_id = fields.Integer(
        string="Resource", required=True, index=True, readonly=True)

    _sql_constraints = [
        ('unique_model', 'UNIQUE(res_model, res_id)',
         'Model instance must be unique')
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.res_model and record.res_id:
                # This case, when resource model is not present in pool, may
                # happen, when addon that implements resource was uninstalled.
                # TODO: handle this in better way
                try:
                    ResourceModel = self.env[record.res_model]
                except KeyError:
                    name = _("Error: no model")
                else:
                    name = ResourceModel.browse(record.res_id).display_name

                result.append((record.id, name))
            else:
                result.append((record.id, False))
        return result

    @api.depends('implementation_ids')
    def _compute_implementation_count(self):
        for rec in self:
            rec.implementation_count = len(rec.implementation_ids)

    @api.model
    def _get_resource_type_defaults(self, resource_type):
        return {
            'res_type_id': resource_type.id,
        }

    @api.model
    def create(self, vals):
        res_id = vals.get('res_id')
        if res_id and isinstance(res_id, GenericResourceResID):
            vals['res_id'] = int(res_id)
        elif res_id:
            raise exceptions.ValidationError(_(
                "Direct creation of 'generic.resource' records "
                "is not allowed!"))

        return super(GenericResource, self).create(vals)

    @api.multi
    def write(self, vals):
        res_id = vals.get('res_id')
        if res_id and isinstance(
                res_id, GenericResourceResID) and len(vals) == 1:
            vals['res_id'] = int(res_id)
            return super(GenericResource, self.sudo()).write(vals)

        elif res_id:
            raise exceptions.ValidationError(_(
                "Direct modification of 'generic.resource:res_id' field "
                "is not allowed!"))

        return super(GenericResource, self).write(vals)
