from odoo import models, fields, api


class GenericConditionDomainLeaf(models.Model):
    _name = 'generic.condition.domain.leaf'
    _order = 'sequence ASC, id ASC'
    _description = 'Generic Condition: Domain Leaf'

    sequence = fields.Integer(default=5, index=True)
    condition_id = fields.Many2one(
        'generic.condition', required=True, index=True, auto_join=True,
        ondelete='cascade')
    type = fields.Selection(
        [('operator-and', 'AND'),
         ('operator-or', 'OR'),
         ('search-condition', 'Condition')],
        required=True)
    check_field_id = fields.Many2one(
        'ir.model.fields', ondelete='cascade')
    check_field_type = fields.Selection(
        related='check_field_id.ttype', readonly=True)
    value_field_id = fields.Many2one(
        'ir.model.fields', ondelete='cascade')
    value_field_operator = fields.Selection(
        [('=', '='),
         ('!=', '!=')])

    @api.onchange('type')
    def _onchange_cleanup_model_fields(self):
        if self.type != 'search-condition':
            self.check_field_id = False
            self.value_field_id = False

    @api.onchange('condition_id', 'check_field_id')
    def _onchange_check_field_id(self):
        if self.check_field_id.ttype in ('many2one',
                                         'many2many',
                                         'one2many'):
            if self.check_field_id.relation != self.value_field_id.relation:
                self.value_field_id = False
            return {
                'domain': {
                    'value_field_id': [
                        ('model_id', '=', self.condition_id.model_id.id),
                        ('ttype', 'in', ('many2one', 'one2many', 'many2many')),
                        ('relation', '=', self.check_field_id.relation),
                    ],
                }
            }

    def _get_domain_leaf_for(self, val_obj):
        self.ensure_one()
        # TODO: Add check to ensure correct model is used
        check_ftype = self.sudo().check_field_id.ttype
        val_ftype = self.sudo().value_field_id.ttype
        operator = self.value_field_operator
        if check_ftype == 'many2one' and val_ftype == 'many2one':
            return [(
                self.sudo().check_field_id.name,
                operator,
                val_obj[self.sudo().value_field_id.name].id,
            )]
        if check_ftype == 'many2one' and val_ftype in ('many2many',
                                                       'one2many'):
            if operator == '=':
                operator = 'in'
            elif operator == '!=':
                operator = 'not in'
            return [(
                self.sudo().check_field_id.name,
                operator,
                val_obj[self.sudo().value_field_id.name].ids,
            )]
        if val_ftype == 'many2one' and check_ftype in ('many2many',
                                                       'one2many'):
            if operator == '=':
                operator = 'in'
            elif operator == '!=':
                operator = 'not in'
            return [(
                '%s.id' % self.sudo().check_field_id.name,
                operator,
                [val_obj[self.sudo().value_field_id.name].id],
            )]
        if (val_ftype in ('many2many', 'one2many') and
              check_ftype in ('many2many', 'one2many')):
            if operator == '=':
                operator = 'in'
            elif operator == '!=':
                operator = 'not in'
            return [(
                '%s.id' % self.sudo().check_field_id.name,
                operator,
                val_obj[self.sudo().value_field_id.name].ids,
            )]

        # Other normal fields
        return [(
            self.sudo().check_field_id.name,
            operator,
            val_obj[self.sudo().value_field_id.name],
        )]

    def compute_domain_for(self, val_obj):
        res = []
        for record in self:
            if record.type == 'operator-and':
                res += ['&']
            elif record.type == 'operator-or':
                res += ['|']
            elif record.type == 'search-condition':
                res += record._get_domain_leaf_for(val_obj)
        return res
