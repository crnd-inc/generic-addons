import logging

from odoo import models

_logger = logging.getLogger(__name__)


class GenericLocation(models.Model):
    _name = 'generic.location'
    _inherit = [
        'generic.location',
        'generic.mixin.uuid',
    ]
    _generic_mixin_uuid_auto_add_field = True

    _sql_constraints = [
        ('uuid_uniq',
         'UNIQUE (uuid)',
         'uuid must be unique.'),
    ]

    def _add_sql_constraints(self):
        _logger.warning('\n\n _ADD_SQL_CONSTRAINTS GenericLocation \n %s\n\n',
                        (self._sql_constraints))
        _logger.warning('\n\n Vals ALL RECORDS \n %s\n\n',
                        (self.search([]).read(['id', 'uuid'])))
        res = super(GenericLocation, self)._add_sql_constraints()
        return res
