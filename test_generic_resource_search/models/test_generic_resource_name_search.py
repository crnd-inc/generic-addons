from odoo import models, fields


class TestGenericResourceNameSearch(models.Model):
    _name = "test.generic.resource.name.search"
    _inherit = [
        "generic.resource.related.mixin",
    ]

    name = fields.Char()
