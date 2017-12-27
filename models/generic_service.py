from openerp import models, fields


class GenericSerivce(models.Model):
    _name = 'generic.service'
    _description = 'Generic Service'

    name = fields.Char(translate=True, required=True, index=True)
    active = fields.Boolean(default=True, index=True)
