# -*- coding: utf-8 -*-
from openerp import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line",
                "generic.tag.mixin"]
