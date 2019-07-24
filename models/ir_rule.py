from odoo import api, models, SUPERUSER_ID
from odoo.osv import expression


class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _generic_res__get_domain(self, mode):
        """ Get domain for generic resources
        """
        return expression.OR([
            # Internal users
            expression.AND([
                [('resource_visibility', 'in', ('internal',
                                                'portal',
                                                'public'))],
                [(int(not self.env.user.share), '=', 1)],
            ]),
            # Portal users
            expression.AND([
                [('resource_visibility', 'in', ('portal', 'public'))],
                [(int(self.env.user.has_group('base.group_portal')), '=', 1)],
            ]),
            # Public users
            expression.AND([
                [('resource_visibility', '=', 'public')],
                [(int(self.env.user.has_group('base.group_public')), '=', 1)],
            ]),
        ])

    @api.model
    def domain_get(self, model_name, mode='read'):
        clauses, params, tables = super(IrRule, self).domain_get(
            model_name, mode=mode)

        # Here we apply custom domain only for mode 'read'
        # For creation standard odoo rules have to be applied
        # Write/Unlink checked in 'check_access_rule' method of
        # generic.resource.
        if model_name == 'generic.resource' and mode == 'read':
            # Do not apply domain for superuser
            if self.env.user.id == SUPERUSER_ID:
                return clauses, params, tables

            # Do not apply restrictions for Resource Manager
            if self.env.user.has_group(
                    'generic_resource.group_generic_resource_manager'):
                return clauses, params, tables

            res_domain = self._generic_res__get_domain(mode)
            res_query = self.env['generic.resource'].sudo()._where_calc(
                res_domain, active_test=False)

            clauses += res_query.where_clause
            params += res_query.where_clause_params
            for res_table in res_query.tables:
                if res_table not in res_query.tables:
                    tables += res_table

        return clauses, params, tables
