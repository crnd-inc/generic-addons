""" Utilities aiming to help to convert various objects to resources
"""
from psycopg2 import sql
from odoo.tools.sql import (
    create_column,
    column_exists,
)


def get_or_create_resource_type(cr, xmlid, model, visibility='internal'):
    """ Find or create resource type for model

        :param str xmlid: xmlid of resource type. must contain module name
        :param str model: name of model for this resource type
        :return int: ID of resource type
    """
    module, name = xmlid.split('.')
    cr.execute("""
        SELECT res_id FROM ir_model_data
        WHERE name=%(name)s
          AND module=%(module)s;
    """, {
        'name': name,
        'module': module,
    })
    type_id = cr.fetchone()
    if type_id:
        return type_id

    cr.execute("""
        SELECT id, name FROM ir_model
        WHERE model=%(model)s
    """, {
        'model': model,
    })
    model_id, model_name = cr.fetchone()

    cr.execute("""
        INSERT INTO generic_resource_type
        (name, model_id, resource_visibility, active)
        VALUES (%(name)s, %(model_id)s, %(visibility)s, True)
        RETURNING id;
    """, {
        'name': model_name,
        'model_id': model_id,
        'visibility': visibility,
    })
    type_id = cr.fetchone()[0]
    cr.execute("""
        INSERT INTO ir_model_data
        (name, module, model, res_id)
        VALUES (%(name)s, %(module)s, %(model)s, %(id)s);
    """, {
        'name': name,
        'module': module,
        'model': 'generic.resource.type',
        'id': type_id,
    })
    return type_id


def create_generic_resources(cr, rtype_id, table, visibility):
    if column_exists(cr, table, 'resource_id'):
        return
    create_column(cr, table, 'resource_id', 'INT')

    # pylint: disable=sql-injection
    cr.execute(
        sql.SQL("SELECT array_agg(id) FROM {}").format(sql.Identifier(table)))
    record_ids = cr.fetchone()[0]
    if not record_ids:
        return

    for record_id in record_ids:
        cr.execute("""
            INSERT INTO generic_resource
            (res_type_id, res_id, resource_visibility, active)
            VALUES (%(type_id)s, %(res_id)s, %(visibility)s, True)
            RETURNING id;
        """, {
            'type_id': rtype_id,
            'res_id': record_id,
            'visibility': 'internal',
        })
        resource_id = cr.fetchone()[0]
        cr.execute(
            sql.SQL("""
                UPDATE {}
                SET resource_id=%(resource_id)s
                WHERE id=%(record_id)s
            """).format(sql.Identifier(table)),
            {
                'resource_id': resource_id,
                'record_id': record_id,
            }
        )


def convert_object_to_resource(cr, type_xml_id, model,
                               table, visibility='internal'):
    rtype_id = get_or_create_resource_type(
        cr, type_xml_id, model, visibility)
    create_generic_resources(cr, rtype_id, table, visibility)
