# -*- coding: utf-8 -*-
from openerp import api, models, _
from openerp.exceptions import ValidationError
from openerp.osv import expression


# Inspired by default product.category implementation
class GenericMixinParentNames(models.AbstractModel):
    """ Simple class to add generic name_get / name_search
        to models that have parent / child relationship

        To use it, just inherit from `generic.mixin.parent.names`
        which have already implemented name_get, name_search and
        recursion check constraint
    """
    _name = "generic.mixin.parent.names"

    # Overridden to add recursion check constraint
    @classmethod
    def _build_model(cls, pool, cr):
        if cls._parent_name:
            @api.constrains(cls._parent_name)
            def _recursion_constraint(self):
                if not self._check_recursion():
                    raise ValidationError(_(
                        'Error ! You cannot create recursive %s.'
                        '') % self._description)
            cls._check_parent_recursion_recursion = _recursion_constraint

        return super(GenericMixinParentNames, cls)._build_model(pool, cr)

    @api.multi
    def name_get(self):
        def get_names(rec):
            """ Return the list [rec.name, rec.parent_id.name, ...] """
            res = []
            while rec:
                res.append(rec[self._rec_name_fallback()])
                rec = rec[self._parent_name]
            return res

        return [(rec.id, " / ".join(reversed(get_names(rec)))) for rec in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            record_names = name.split(' / ')
            parents = list(record_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args,
                                             operator='ilike', limit=limit)
                record_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    records = self.search([('id', 'not in', record_ids)])
                    domain = expression.OR(
                        [[(self._parent_name, 'in', records.ids)], domain])
                else:
                    domain = expression.AND(
                        [[(self._parent_name, 'in', record_ids)], domain])
                for i in range(1, len(record_names)):
                    names = ' / '.join(record_names[-1 - i:])
                    domain = [[('name', operator, names)], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            records = self.search(expression.AND([domain, args]), limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.name_get()
