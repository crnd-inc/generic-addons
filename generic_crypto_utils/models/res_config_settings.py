from odoo import models, api

CRYPTO_PLACEHOLDER = '******'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _get_classified_fields(self):
        """ return a dictionary with the fields classified by category::

                {   'default': [('default_foo', 'model', 'foo'), ...],
                    'group':   [('group_bar',
                                [browse_group],
                                browse_implied_group), ...],
                    'module':  [('module_baz', browse_module), ...],
                    'config':  [('config_qux', 'my.parameter'), ...],
                    'crypto';  [('crypto_xyz', 'param.name'),...],
                    'other':   ['other_field', ...],
                }
        """
        res = super()._get_classified_fields()

        others = set(res['other'])
        # Find fields that are crypto params
        crypto_params = []
        for name, field in self._fields.items():
            if hasattr(field, 'crypto_param'):
                if field.type not in ('char', 'text'):
                    raise Exception(
                        "Field %s must have type 'char' or 'text'" % field)
                crypto_params.append((name, field.crypto_param))
                others.remove(name)

        res.update({
            'other': list(others),
            'crypto': crypto_params,
        })

        return res

    @api.model
    def default_get(self, fields):
        res = super(ResConfigSettings, self).default_get(fields)

        classified = self._get_classified_fields()
        for name, __ in classified['crypto']:
            # TODO: add option, that could control whether we need to display
            # encrypted value or keep it hidden
            res[name] = CRYPTO_PLACEHOLDER

        return res

    def set_values(self):
        """
        Set values for the fields other that `default`, `group` and `module`
        """
        res = super().set_values()
        classified = self._get_classified_fields()
        for name, param_name in classified['crypto']:
            if self[name] != CRYPTO_PLACEHOLDER:
                self.env['generic.crypto.param'].set_param(
                    param_name, self[name])
        return res

    def _valid_field_parameter(self, field, name):
        # Make crypto_param field attribute valid for this model
        if name == 'crypto_param':
            return True
        return super()._valid_field_parameter(field, name)
