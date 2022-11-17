def xmlid_to_id(cr, xmlid):
    """ Resolve XMLIO to ID of object it references

        :param cr: database cursor
        :param str xmlid: string representing external identifier (xmlid)
            of object. It must be fully qualified xmlid, that includes
            name of module.
        :return int|bool: ID of object if such xmlid exists,
            or False if there is no such xmlid registered in db.
    """
    module, name = xmlid.split('.', 1)
    cr.execute("""
        SELECT res_id
        FROM ir_model_data
        WHERE module = %(module)s
          AND name = %(name)s
    """, {
        'module': module,
        'name': name,
    })
    if cr.rowcount > 0:
        return cr.fetchone()[0]
    return False


def get_xmlid(cr, model, res_id):
    """ Return XMLID for specified record (res_id) in specified model

        :param cr: database cursor
        :param str model: model to search xmlid for
        :param int res_id: ID of record to get XML ID for
        :return (str, str): tuple with module name and xmlid
    """
    cr.execute("""
        SELECT module, name
        FROM ir_model_data
        WHERE model = %(model)s
          AND res_id = %(res_id)s
        LIMIT 1
    """, {
        'model': model,
        'res_id': res_id,
    })
    res = cr.fetchone()
    if not res:
        return False, False
    return res


def register_xmlid(cr, module, name, model, res_id):
    """ Insert new record into ir_model_data

        :param cr: Database cursor
        :param str module: Name of module for xmlid
        :param str name: Name of xmlid
        :param str model: name of model to reference
        :param int res_id: ID of record to register xmlid for.
    """
    cr.execute("""
        INSERT INTO ir_model_data
                (module, name, model, res_id)
        VALUES (%(module)s, %(name)s,
                %(model)s, %(res_id)s);
    """, {
        'model': model,
        'module': module,
        'name': name,
        'res_id': res_id,
    })


def update_xmlid(cr, module, name, model, res_id):
    """ Update ir_model_data record specified by module and name,
        with new model and res_id

        :param cr: Database cursor
        :param str module: Name of module for xmlid
        :param str name: Name of xmlid
        :param str model: name of model to reference
        :param int res_id: ID of record.
    """
    cr.execute("""
        UPDATE ir_model_data
        SET model = %(model)s, res_id = %(res_id)s
        WHERE module = %(module)s
          AND name = %(name)s;
    """, {
        'model': model,
        'module': module,
        'name': name,
        'res_id': res_id,
    })
