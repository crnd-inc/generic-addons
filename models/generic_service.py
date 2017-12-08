from openerp import models, fields, api


class GenericSerivce(models.Model):
    _name = 'generic.service'

    name = fields.Char(translate=True, required=True, index=True)
    active = fields.Boolean(default=True, index=True)
    product_id = fields.Many2one(
        'product.product', domain=[('type', '=', 'service')], string="Product",
        ondelete='restrict', required=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.name = rec.product_id.name
