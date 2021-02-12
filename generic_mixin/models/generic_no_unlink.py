from odoo import models, _
from odoo.osv.expression import FALSE_DOMAIN
from odoo.exceptions import UserError


class GenericMixinNoUnlink(models.AbstractModel):
    """ This model adds generic logic, that prevents unlink of model records
    """
    _name = 'generic.mixin.no.unlink'
    _description = "Generic Mixin: No Unlink"

    # Change this domain to that one, that selected records allowed to be
    # unlinked
    _allow_unlink_domain = FALSE_DOMAIN

    def _allow_unlink(self):
        """ Decide whether unlink of selected records is allowed or not

            By default unlink not allowed at all.

            It is possible to set `_allow_unlink_domain` on model,
            to select records that are allowed to be unlinked.
        """
        allowed_count = self.search_count(
            [('id', 'in', self.ids)] + self._allow_unlink_domain
        )
        return allowed_count == len(self.exists())

    def unlink(self):
        if not self._allow_unlink():
            if 'active' in self._fields:
                raise UserError(_(
                    "Cannot unlink these records. Operation not allowed.\n"
                    "It is better to deactivate these records.\n"
                    "Model: %(model)s [%(model_name)s]"
                ) % {
                    'model': self._name,
                    'model_name': self._description,
                })
            raise UserError(_(
                "Cannot unlink these records. Operation not allowed.\n"
                "Model: %(model)s [%(model_name)s]"
                ) % {
                    'model': self._name,
                    'model_name': self._description,
                })

        return super(GenericMixinNoUnlink, self).unlink()
