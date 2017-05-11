from openerp import models, fields, api

class Product(models.Model):
    _name = "product.product"
    _inherit = ["product.product",
                "res.tag.mixin"]
