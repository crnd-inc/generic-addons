from odoo import models


class Product(models.Model):
    _name = "product.product"
    _inherit = ["product.product",
                "generic.tag.mixin"]
