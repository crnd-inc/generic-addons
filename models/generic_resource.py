import logging
from odoo import fields, models, api, exceptions, _

_logger = logging.getLogger(__name__)


class GenericResourceResID(int):
    """ Simple class to ensure that 'generic.resource' being created
        from 'generic.resource.mixin' code
    """


class GenericResource(models.Model):
    _name = 'generic.resource'
    _description = 'Generic Resource'
    _log_access = False

    active = fields.Boolean(default=True, index=True)
    res_type_id = fields.Many2one(
        'generic.resource.type', string="Type", required=True, index=True,
        ondelete='cascade')
    res_model = fields.Char(
        related='res_type_id.model_id.model', readonly=True, store=True,
        compute_sudo=True, index=True)
    res_id = fields.Integer(
        string="Resource", required=True, index=True, readonly=True)
    resource_visibility = fields.Selection(
        [('internal', 'Visible only to employees'),
         ('portal', 'Visible to employees and portal users'),
         ('public', 'Visible for unregistered users')],
        default='internal', required=True, index=True,
        help="Resource visibility determines users that have read access for "
             "this resource.")

    _sql_constraints = [
        ('unique_model', 'UNIQUE(res_model, res_id)',
         'Model instance must be unique')
    ]

    @property
    def resource(self):
        """ Property to easily access implementation of this generic resource
        """
        self.ensure_one()
        # This case, when resource model is not present in pool, may
        # happen, when addon that implements resource was uninstalled.
        # TODO: handle this in better way
        try:
            ResourceModel = self.env[self.res_model]
        except KeyError:
            return False
        resource = ResourceModel.browse(self.res_id)
        if resource.exists():
            return resource
        return False

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.res_model and record.res_id:
                if record.resource:
                    result.append((record.id, record.resource.display_name))
                else:
                    result.append((record.id, _("Error: no model")))
            else:
                result.append((record.id, False))
        return result

    @api.model
    def _get_resource_type_defaults(self, resource_type):
        return {
            'res_type_id': resource_type.id,
            'resource_visibility': resource_type.resource_visibility,
        }
    @api.multi
    def _preprocess_resource_changes(self, changes):
        """ This method is called before write on resource implementation and
            receives dict with changes of tracked fields.

            This method may be overridden by other modules to add
            some postprocessing of resource changes.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :rtype: dict
            :return: values to update record with.
                     These values will be written just after write
        """
        return {}

    @api.multi
    def _postprocess_resource_changes(self, changes):
        """ This method is called adter write on resource implementation and
            receives dict with changes of tracked fields.

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any  value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """
        pass

    @api.model
    def default_get(self, fields_list):
        res = super(GenericResource, self).default_get(fields_list)

        if 'generic_resource_type_model' in self.env.context:
            res_type = self.env['generic.resource.type'].get_resource_type(
                self.env.context['generic_resource_type_model'])
            res.update({
                k: v
                for k, v in self._get_resource_type_defaults(res_type).items()
                if k in fields_list
            })
        return res

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

        if res_id:
            raise exceptions.ValidationError(_(
                "Direct modification of 'generic.resource:res_id' field "
                "is not allowed!"))

        return super(GenericResource, self).write(vals)

    @api.multi
    def on_resource_created(self):
        """ Hook to be called when resource creation completed
        """
        pass

    @api.multi
    def action_open_resource_object(self):
        if self.resource:
            return self.resource.get_formview_action()
