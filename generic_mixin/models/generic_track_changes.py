import collections
from odoo import models, api


class GenericMixInTrackChanges(models.AbstractModel):
    _name = 'generic.mixin.track.changes'
    _description = 'Generic Mixin: Track Changes'

    @api.model
    def _get_generic_tracking_fields(self):
        """ Compute set of filed to track changes.

            :rtype: set
            :return: set of fields track changes of
        """
        return set()

    @api.multi
    def _get_changed_fields(self, vals):
        """ Preprocess vals to be written, and gether field changes
        """
        field_names = self._get_generic_tracking_fields()
        changes = collections.defaultdict(dict)
        changed_fields = set(field_names) & set(vals.keys())
        if changed_fields:
            # changes = {
            #     record_id: {
            #         field1: (old_value, new_value),
            #     }
            # }
            for record in self:
                for field in changed_fields:
                    old_value = record[field]
                    new_value = self._fields[field].convert_to_record(
                        self._fields[field].convert_to_cache(
                            vals[field], self),
                        self)
                    if old_value != new_value:
                        changes[record.id][field] = (old_value,
                                                     new_value)
        return dict(changes)

    @api.multi
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
        self.ensure_one()
        return {}

    @api.multi
    def _postprocess_write_changes(self, changes):
        """ Called after write

            This method may be overridden by other modules to add
            some postprocessing of write.
            This method does not return any  value.

            :param dict changes: keys are changed field names,
                                 values are tuples (old_value, new_value)
            :return: None

        """

        self.ensure_one()

    @api.multi
    def write(self, vals):
        changes = self._get_changed_fields(vals)

        # Store here updates got from preprocessing
        updates = collections.defaultdict(dict)
        for record in self:
            if record.id in changes:
                updates[record.id] = record._preprocess_write_changes(
                    changes[record.id])

        res = super(GenericMixInTrackChanges, self).write(vals)

        # Update records (using values from pre-processing) and apply post
        # processing
        for record in self:
            if record.id in updates:
                super(GenericMixInTrackChanges, record).write(
                    updates[record.id])
            if record.id in changes:
                record._postprocess_write_changes(changes[record.id])
        return res
