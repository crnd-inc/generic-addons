from odoo import models, fields, api, exceptions, _

from odoo.addons.generic_m2o.tools.utils import generic_m2o_get


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
        related='check_field_id.ttype', readonly=True,
        compute_sudo=True)
    check_field_relation = fields.Char(
        related='check_field_id.relation', readonly=True,
        compute_sudo=True)
    value_field_operator = fields.Selection(
        [('=', '=')])
    value_type = fields.Selection(
        [('object-field', 'Object Field'),
         ('static-value', 'Static Value')],
        help="Object Field: uses value from field of the object being checked."
             "Static Value: static value to check.")
    value_field_id = fields.Many2one(
        'ir.model.fields', ondelete='cascade')
    value_boolean = fields.Selection(
        [('true', 'True'), ('false', 'False')])
    value_char = fields.Char()
    value_float = fields.Float()
    value_integer = fields.Integer()
    value_selection = fields.Char()
    value_res_id = fields.Integer()

    value_display = fields.Char(
        compute='_compute_value_display', readonly=True)

    @api.depends('value_type', 'value_field_id', 'value_boolean', 'value_char',
                 'value_float', 'value_integer', 'value_selection',
                 'value_res_id', 'check_field_type', 'check_field_relation',
                 'check_field_id')
    def _compute_value_display(self):
        for record in self:
            if record.value_type == 'object-field':
                record.value_display = (
                    record.sudo().value_field_id.display_name)
            elif record.value_type == 'static-value':
                if record.check_field_type in ('char', 'text', 'html'):
                    record.value_display = record.value_char
                elif record.check_field_type == 'float':
                    record.value_display = record.value_float
                elif record.check_field_type == 'integer':
                    record.value_display = record.value_integer
                elif record.check_field_type == 'selection':
                    record.value_display = record.value_selection
                elif record.check_field_type in ('many2one',
                                                 'one2many',
                                                 'many2many'):
                    record.value_display = generic_m2o_get(
                        record,
                        field_res_model="check_field_relation",
                        field_res_id="value_res_id",
                    ).display_name
                else:
                    record.value_display = ""
            else:
                record.value_display = ""

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
        return {}

    def _get_domain_leaf_for_object_field(self, val_obj):
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
            return [(
                self.sudo().check_field_id.name,
                operator,
                val_obj[self.sudo().value_field_id.name].ids,
            )]
        if val_ftype == 'many2one' and check_ftype in ('many2many',
                                                       'one2many'):
            if operator == '=':
                operator = 'in'
            return [(
                '%s.id' % self.sudo().check_field_id.name,
                operator,
                [val_obj[self.sudo().value_field_id.name].id],
            )]
        if (val_ftype in ('many2many', 'one2many') and
                check_ftype in ('many2many', 'one2many')):
            if operator == '=':
                operator = 'in'
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

    def _get_domain_leaf_for_static_field(self, val_obj):
        check_ftype = self.sudo().check_field_id.ttype
        operator = self.value_field_operator
        if check_ftype in ('char', 'text', 'html'):
            value = self.value_char
        elif check_ftype == 'integer':
            value = self.value_integer
        elif check_ftype == 'float':
            value = self.value_float
        elif check_ftype == 'selection':
            value = self.value_selection
        elif check_ftype in ('many2one', 'one2many', 'many2many'):
            value = self.value_res_id
        else:
            raise exceptions.UserError(_(
                "Currently it is not supported to check "
                "fields of %(field_type)s type "
                "with static value"
            ) % {
                "field_type": check_ftype,
            })

        return [(self.sudo().check_field_id.name, operator, value)]

    def _get_domain_leaf_for(self, val_obj):
        self.ensure_one()
        if self.value_type == 'object-field':
            return self._get_domain_leaf_for_object_field(val_obj)
        if self.value_type == 'static-value':
            return self._get_domain_leaf_for_static_field(val_obj)

        # TODO: May be raise error here
        return []

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
