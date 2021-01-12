from odoo import models, fields, api, _


class GenericMixinNameBySequence(models.AbstractModel):
    """ Simple mixin to add automatic name generation by sequence for object.

        To use, just do following steps:
        1. inherit your model from this mixin,
        2. If needed enable automatic creation of name field:
            "_name_by_sequence_auto_add_field = True"
        3. Specify code of sequence to be used to generate names:
            "_name_by_sequence_sequence_code = 'my.sequence.code'"

        After this, you will get 'name' field, that will contain automatically
        generated value.
    """
    _name = 'generic.mixin.name.by.sequence'
    _description = 'Generic Mixin: Name by Sequence'

    _name_by_sequence_name_field = 'name'
    _name_by_sequence_auto_add_field = False
    _name_by_sequence_sequence_code = None

    @api.model
    def _name_by_sequence_get_default_value(self):
        return _('New')

    @api.model
    def _add_magic_fields(self):
        res = super(GenericMixinNameBySequence, self)._add_magic_fields()

        if not self._name_by_sequence_auto_add_field:
            return res

        name_field_name = self._name_by_sequence_name_field
        if name_field_name not in self._fields:
            self._add_field(
                name_field_name,
                fields.Char(
                    readonly=True, index=True,
                    required=True, copy=False,
                    default=lambda s: s._name_by_sequence_get_default_value())
            )
        return res

    def _name_by_sequence_update_name_in_vals(self, vals):
        """ Set name in values provided to 'create' method
        """
        if not self._name_by_sequence_name_field:
            return vals

        if self._name_by_sequence_name_field not in self._fields:
            return vals

        if not self._name_by_sequence_sequence_code:
            return vals

        fname = self._name_by_sequence_name_field
        fdefault = self._name_by_sequence_get_default_value()
        fsequence = self._name_by_sequence_sequence_code

        if vals.get(fname, fdefault) == fdefault:
            vals = dict(vals)
            vals[fname] = self.env['ir.sequence'].next_by_code(
                fsequence) or fdefault
        return vals

    # TODO: add support for batch create
    @api.model
    def create(self, vals):
        vals = self._name_by_sequence_update_name_in_vals(vals)
        return super(GenericMixinNameBySequence, self).create(vals)
