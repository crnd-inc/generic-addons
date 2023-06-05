from odoo import api


def l_parent_get_field_names(field_name):
    """ Compute names of additional fields that take part
        in computation of location's parent-based address fields.

        Return tuple with following names of companion fields:
        - hidden_field - name of field that actually stores value
        - check_field - name of field that determines use parent value or not

        :param str field_name: name of field to get companion fields for
        :return tuple: tuple with 2 names of fields in following order:
            hidden_field, check_field
    """
    hidden_field = '_%s' % field_name
    check_field = '%s_use_parent' % field_name
    return hidden_field, check_field


def l_parent_get_value(record, field_name):
    """ Compute the value for specified field, depending on
        the configuration.

        If the field is configured to use value from parent location,
        then this function will recursively call computation of
        value for this field for parent record.

        Note, that this function is needed to implement recursion.
    """

    hfield, cfield = l_parent_get_field_names(field_name)

    if record[cfield] and record['parent_id']:
        return l_parent_get_value(record.parent_id, field_name)
    return record[hfield]


def l_parent_compute(field_name):
    """ Compute location address fields based on location's parent
    """
    hfield, cfield = l_parent_get_field_names(field_name)

    @api.depends(hfield, cfield, 'parent_id', 'parent_ids',
                 'parent_id.%s' % field_name)
    def _compute_func(self):
        for record in self:
            record[field_name] = l_parent_get_value(
                record.sudo(), field_name)
    return _compute_func


def l_parent_inverse(field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    def _inverse_func(self):
        for record in self:
            if not record[cfield]:
                record[hfield] = record[field_name]
    return _inverse_func
