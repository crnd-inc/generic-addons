from odoo import models, fields, api


class GenericTagWizardManageTags(models.TransientModel):
    _name = 'generic.tag.wizard.manage.tags'
    _description = 'Generic Tag Wizard: Manage Tags'

    @api.model
    def _get_default_model_id(self):
        default_model = self.env.context.get('manage_tags_model', False)

        if default_model:
            return self.env['generic.tag.model'].search(
                [('model', '=', default_model)], limit=1)

        return self.env['generic.tag.model'].browse()

    model_id = fields.Many2one(
        'generic.tag.model', required=True, ondelete='cascade',
        default=_get_default_model_id)
    tag_ids = fields.Many2many(
        'generic.tag', required=True)
    action = fields.Selection(
        [('add', 'Add'),
         ('set', 'Set'),
         ('remove', 'Remove')],
        required=True, default='add')

    def do_apply(self):
        self.ensure_one()

        records = self.env[self.model_id.model].search(
            [('id', 'in', self.env.context.get('manage_tags_object_ids', []))])

        for record in records:
            if self.action == 'add':
                record.tag_ids += self.tag_ids
            elif self.action == 'set':
                record.tag_ids = self.tag_ids
            elif self.action == 'remove':
                record.tag_ids -= self.tag_ids
