from openerp.osv import orm

class Product(orm.Model):
    _name = "product.product"
    _inherit = ["product.product",
                "res.tag.mixin"]

Product()
