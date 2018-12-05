from odoo import models


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice",
                "generic.tag.mixin"]
