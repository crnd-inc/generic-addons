from odoo import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'
    _inherit = [
        'mail.thread',
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'generic.mixin.get.action',
    ]
    _description = 'Generic Service'
    _order = 'sequence, name'

    name = fields.Char(track_visibility='always')
    active = fields.Boolean(
        default=True, index=True, track_visibility='onchange')
    description = fields.Text(translate=True)
    sequence = fields.Integer(index=True, default=5)
    change_manager_id = fields.Many2one('res.users', ondelete='restrict')
