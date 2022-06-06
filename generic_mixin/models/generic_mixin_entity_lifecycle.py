from odoo import models, fields, exceptions, _
from .generic_track_changes import pre_write


class GenericMixinEntityLifecycle(models.AbstractModel):
    """ Simple mixin to provide basic fields and logic
        for entities lifecycle.

        Currently, each entity could have following states:
            - Draft
            - Active
            - Obsolete
            - Archived

        Also, this mixin prevents deletion of non-draft records
    """
    _name = 'generic.mixin.entity.lifecycle'
    _inherit = [
        'generic.mixin.track.changes',
        'generic.mixin.no.unlink'
    ]
    _description = 'Generic Mixin: Entity Lifecycle'

    _allow_unlink_domain = [('lifecycle_state', '=', 'draft')]

    lifecycle_state = fields.Selection(
        [('draft', 'Draft'),
         ('active', 'Active'),
         ('obsolete', 'Obsolete'),
         ('archived', 'Archived')],
        required=True, default='draft', index=True, readonly=True)
    lifecycle_date_created = fields.Datetime(
        default=fields.Datetime.now, readonly=True)
    lifecycle_date_activated = fields.Datetime(readonly=True)
    lifecycle_date_obsolete = fields.Datetime(readonly=True)
    lifecycle_date_archived = fields.Datetime(readonly=True)

    def _gmel_get_allowed_state_changes(self):
        return {
            'draft': ['active'],
            'active': ['obsolete'],
            'obsolete': ['archived'],
            'archived': [],
        }

    @pre_write('lifecycle_state')
    def _gmel_update_entity_on_state_change(self, changes):
        old_state, new_state = changes['lifecycle_state']
        allowed_new_states = self._gmel_get_allowed_state_changes().get(
            old_state, [])
        if new_state not in allowed_new_states:
            raise exceptions.ValidationError(_(
                "It is not allowed to change Lifecycle State field"
                "from %(old_state)s to %(new_state)s!\n"
                "Allowed next states: %(allowed_states)s"
            ) % {
                'old_state': old_state,
                'new_state': new_state,
                'allowed_states': allowed_new_states,
            })
        res = {}
        if new_state == 'active':
            res['lifecycle_date_activated'] = fields.Datetime.now()
        elif new_state == 'obsolete':
            res['lifecycle_date_obsolete'] = fields.Datetime.now()
        elif new_state == 'archived':
            res['lifecycle_date_archived'] = fields.Datetime.now()
            if self._fields.get('active'):
                # Automatically set active to False on archivation of entity
                res['active'] = False
        return res

    def action_lifecycle_state__activate(self):
        self.write({'lifecycle_state': 'active'})

    def action_lifecycle_state__obsolete(self):
        self.write({'lifecycle_state': 'obsolete'})

    def action_lifecycle_state__archive(self):
        self.write({'lifecycle_state': 'archived'})
