import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class GenericResourceMixin(models.AbstractModel):
    _name = 'generic.resource.mixin'
    _description = 'Generic Resource MixIn'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.delegation.implementation',
    ]

    resource_id = fields.Many2one(
        'generic.resource', index=True, auto_join=True,
        required=True, delegate=True, ondelete='restrict',
        string="Generic Resource")

    _sql_constraints = [
        ('unique_resource_id', 'UNIQUE(resource_id)',
         'Resource must be unique')
    ]

    @api.model
    def _get_generic_tracking_fields(self):
        """ Get tracking fields

            :return set(str): Set of names of fields to track changes
        """
        track_fields = super(
            GenericResourceMixin, self)._get_generic_tracking_fields()
        res_type = self._get_resource_type()
        return track_fields | res_type.get_resource_tracking_fields()

    def _preprocess_write_changes(self, changes):
        """ Called before write

            This method may be overridden by other addons to add
            some preprocessing of changes, before write

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :rtype: dict
            :return: values to update record with.
                     These values will be written just after write
        """
        vals = super(GenericResourceMixin, self)._preprocess_write_changes(
            changes)
        vals.update(self.resource_id._preprocess_resource_changes(changes))
        return vals

    def _postprocess_write_changes(self, changes):
        """ Called after write

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any  value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """
        res = super(GenericResourceMixin, self)._postprocess_write_changes(
            changes)
        self.resource_id._postprocess_resource_changes(changes)
        return res

    @api.model
    def default_get(self, fields_list):
        return super(
            GenericResourceMixin,
            self.with_context(generic_resource_type_model=self._name)
        ).default_get(fields_list)

    @api.model_create_multi
    def create(self, vals):
        values = [
            dict(self._get_resource_type()._get_resource_defaults(), **v)
            for v in vals
        ]

        # Create record
        records = super().create(values)

        # Call 'on_resource_created' hook
        for record in records:
            # TODO: Support multi-record in on_resource_created
            record.resource_id.on_resource_created()
        return records

    def _get_resource_type(self):
        return self.env['generic.resource.type'].get_resource_type(self._name)

    def check_access_rule(self, operation):
        # Overridden to check access to generic resources also
        self.mapped('resource_id').check_access_rule(operation)
        return super(GenericResourceMixin, self).check_access_rule(operation)
