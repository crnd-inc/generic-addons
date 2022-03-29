def generic_m2o_get(record, *, field_res_model, field_res_id):
    """ Utility function to read generic many2one field on specified record.

        :param RecordSet record: Single-record recordset to read m2o field.
        :param str field_res_model: name of field to read name of referenced
            model.
        :param str field_res_id: field that represents ID of referenced record
        :return RecordSet: single-record recordset that represents referenced
            record. In case if referenced model does not exists, may return
            False.
    """
    record.ensure_one()

    # This case, when res model is not present in pool, may
    # happen, when addon that implements this model was uninstalled.
    try:
        Model = record.env[record[field_res_model]]
    except KeyError:
        return False

    res_record = Model.browse(record[field_res_id])
    # generic m2o record may not exist,
    # when referenced record was deleted
    # with ondelete='cascade' on res model
    if res_record.exists():
        return res_record
    return Model.browse()
