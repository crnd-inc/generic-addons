from odoo import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'
    _inherit = [
        'mail.thread',
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'generic.mixin.get.action',
        'generic.mixin.entity.lifecycle',
    ]
    _description = 'Generic Service'
    _order = 'sequence, name'

    name = fields.Char(tracking=True)
    active = fields.Boolean(
        default=True, index=True, tracking=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(index=True, default=5)
    change_manager_id = fields.Many2one('res.users', ondelete='restrict')
    service_group_id = fields.Many2one(
        'generic.service.group',
        index=True,
        ondelete='restrict')

    # Access rignts
    access_group_ids = fields.Many2many(
        'res.groups', string='Access groups',
        help="Restrict access to this service by specified groups only")
