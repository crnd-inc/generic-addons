from odoo import api


def l_parent_get_field_names(field_name):
    hidden_field = '_%s' % field_name
    check_field = '%s_use_parent' % field_name
    return hidden_field, check_field


def l_parent_get_value(record, field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    if record[cfield] and record['parent_id']:
        return l_parent_get_value(record.parent_id, field_name)
    return record[hfield]


def l_parent_compute(field_name):
    hfield, cfield = l_parent_get_field_names(field_name)

    @api.depends(hfield, cfield, 'parent_id')
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
