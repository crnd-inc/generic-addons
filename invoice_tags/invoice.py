from openerp.osv import orm


class Invoice(orm.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice",
                "res.tag.mixin"]

Invoice()
