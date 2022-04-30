import logging
from odoo import api, models, tools
from odoo.osv import expression

_logger = logging.getLogger(__name__)


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
    @tools.conditional(
        'xml' not in tools.config['dev_mode'],
        tools.ormcache('self.env.uid', 'self.env.su', 'model_name', 'mode',
                       'tuple(self._compute_domain_context_values())'),
    )
    def _compute_domain(self, model_name, mode="read"):
        domain = super(IrRule, self)._compute_domain(model_name, mode=mode)

        # Here we apply custom domain only for mode 'read'
        # For creation standard odoo rules have to be applied
        # Write/Unlink checked in 'check_access_rule' method of
        # generic.resource.
        if model_name == 'generic.resource' and mode in ('read', 'create'):
            # Do not apply domain for superuser
            if self.env.su:
                return domain

            # Do not apply restrictions for Resource Manager
            if self.env.user.has_group(
                    'generic_resource.group_generic_resource_manager'):
                return domain

            domain = expression.AND([
                domain,
                self._generic_res__get_domain(mode)
            ])

        return domain
