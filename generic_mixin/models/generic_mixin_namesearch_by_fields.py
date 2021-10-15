from odoo import models, api
from odoo.osv import expression


class GenericMixinNamesearchByFields(models.AbstractModel):
    """ Simple mixin, that allows to easily add ability to search record
        via name_search by some number of fields.

        So, if you want to add support for your model to use fields
        'name' and 'category' in name_search, then you can do following:

        class MyModel:
            _name = 'my.model'
            _inherit = 'generic.mixin.namesearch.by.fields'
            _generic_namesearch_fields = [
                'name',
                'category',
            ]
    """
    _name = 'generic.mixin.namesearch.by.fields'
    _description = 'Generic Mixin: Name search by fields'

    _generic_namesearch_fields = []

    # This param could be used in by other mixins to include '_rec_name' in
    # search
    _generic_namesearch_search_by_rec_name = False

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not self._generic_namesearch_fields:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit)

        if not name:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit)

        # List of domains to search record via
        domains = [
            [(fname, operator, name)]
            for fname in self._generic_namesearch_fields
        ]

        # Optionaly search via rec_name too
        if self._generic_namesearch_search_by_rec_name and self._rec_name:
            domains += [[(self._rec_name, operator, name)]]

        # In case of negative operator (not ilike), we need to join domains
        # via AND operator. For example:
        #     code not ilike 'test' and name not ilike 'test'
        # Contrary in case of positive term operator, we need to use OR to
        # join domains. For example:
        #     code ilike 'test' or name 'ilike' test
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = expression.AND(domains)
        else:
            domain = expression.OR(domains)

        return self.search(
            expression.AND([
                args if args else [],
                domain]),
            limit=limit
        ).sudo().name_get()
