from odoo import fields, models


class ServerAction(models.Model):
    _inherit = "ir.actions.server"

    state = fields.Selection(selection_add=[('set_tag', 'Set Tag')])
