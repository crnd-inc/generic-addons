import collections

from odoo import models, fields, api, exceptions, _

from ..utils import ensure_code_or_name


class GenericTagMixin(models.AbstractModel):
    """ Mixin to be used to add tag support to any model
        by inheriting from it like:
            _inherit=["generic.tag.mixin"]
    """
    _name = "generic.tag.mixin"
    _description = "Generic Tag Mixin"

    @api.constrains('tag_ids')
    def _check_tags_xor(self):
        for record in self:
            categ_counter = collections.defaultdict(
                self.env['generic.tag'].browse)
            for tag in record.tag_ids:
                if tag.category_id.check_xor:
                    categ_counter[tag.category_id] |= tag

            bad_tags = []
            for category, tags in categ_counter.items():
                if len(tags) > 1:
                    bad_tags.append(
                        (category, tags)
                    )
            if bad_tags:
                msg_detail = ', '.join(
                    ('[%s - %s]' % (cat.name, ', '.join(tags.mapped('name')))
                     for cat, tags in bad_tags)
                )
                raise exceptions.ValidationError(
                    _("Following (category - tags) pairs, "
                      "break category XOR restriction:\n%s"
                      "") % msg_detail)

    def _search_no_tag_id(self, operator, value):
        with_tags = self.search([('tag_ids', operator, value)])
        return [('id', 'not in', with_tags.mapped('id'))]

    def _search_tag_id(self, operator, value):
        return [('tag_ids', operator, value)]

    def _compute_search_tag(self):
        for rec in self:
            rec.search_tag_id = False
            rec.search_no_tag_id = False

    tag_ids = fields.Many2many(
        'generic.tag', string="Tags",
        domain=lambda self: [('model_id.model', '=', self._name)])

    # Search capabilities
    search_tag_id = fields.Many2one(
        'generic.tag', string='Tag', compute='_compute_search_tag',
        search='_search_tag_id', store=False, readonly=True,
        domain=lambda self: [('model_id.model', '=', self._name)],
        help="Find all records that contain this tag")
    search_no_tag_id = fields.Many2one(
        'generic.tag', string='No tag', compute='_compute_search_tag',
        search='_search_no_tag_id', store=False, readonly=True,
        domain=lambda self: [('model_id.model', '=', self._name)],
        help="Find all records that have no this tag")

    def add_tag(self, code=None, name=None, create=False):
        """ Adds tag new tag to object.

            @param code: tag.code field to search for
            @param name: tag.name field to search for
            @param create: if True then create tag if not found
        """
        tags = self.env['generic.tag'].get_tags(
            self._name, code=code, name=name)

        if not tags and create:
            model = self.env['generic.tag.model'].search(
                [('model', '=', self._name)])[0]
            tags = self.env['generic.tag'].create({
                'name': name,
                'code': code,
                'model_id': model.id,
            })

        if tags:
            self.write({'tag_ids': [(4, t.id) for t in tags]})

    def remove_tag(self, code=None, name=None):
        """ Removes tags specified by code/name

            @param code: tag.code field to search for
            @param name: tag.name field to search for
        """
        tags = self.env['generic.tag'].get_tags(
            self._name, code=code, name=name)

        if tags:
            self.write({'tag_ids': [(3, t.id) for t in tags]})

    def check_tag(self, code=None, name=None):
        """ Check if self have tag with specified code / name
        """
        ensure_code_or_name(code, name)
        tag_domain = [('id', 'in', self.ids)]
        if code is not None:
            tag_domain.append(('tag_ids.code', '=', code))
        if name is not None:
            tag_domain.append(('tag_ids.name', '=', name))

        count = self.search_count(tag_domain)
        return bool(count == len(self))

    def check_tag_category(self, code=None, name=None):
        """ Checks if self have tag with specified
            category code and/or category name
        """
        ensure_code_or_name(code, name)
        categ_domain = [('id', 'in', self.ids)]
        if code is not None:
            categ_domain.append(('tag_ids.category_id.code', '=', code))
        if name is not None:
            categ_domain.append(('tag_ids.category_id.name', '=', name))

        count = self.search_count(categ_domain)
        return bool(count == len(self))
