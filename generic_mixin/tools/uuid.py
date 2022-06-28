"""
This module will contain various utility functions for migrations
and related tasks.
"""
import uuid
from psycopg2 import sql
from odoo.tools.sql import create_column


def create_uuid_field(cr, table, field_name):
    """ Create new UUID column in table

        :param cr: Database cursor
        :param str table: Name of table to add column to
        :param str field_name: Name of column to add to table
    """
    create_column(cr, table, field_name, 'character varying(38)')


def generate_uuid_for_table(cr, table, field_name):
    """ Generate new unique UUID for table in specified column

        :param cr: Database cursor
        :param str table: Name of table to generate new UUID for
        :param str field_name: Name of field to generate new UUID for
        :return str: New generated UUID
    """
    new_uuid_ok = False
    while not new_uuid_ok:
        new_uuid = str(uuid.uuid4())

        # Ensure that uuid is unique
        cr.execute(sql.SQL("""
            SELECT EXISTS (
                SELECT 1
                FROM {table}
                WHERE {field_name} = %(uuid)s
            )
        """).format(
            table=sql.Identifier(table),
            field_name=sql.Identifier(field_name),
        ), {'uuid': new_uuid})
        if not cr.fetchone()[0]:
            new_uuid_ok = True
    return new_uuid


def auto_generate_uuids(cr, table, field_name):
    """ Automatically generate uuids for existing records in specified table

        :param cr: Database cursor
        :param str table: Name of table to generate uuids for
        :param str field_name: Name of field to generate UUIDs for
    """
    cr.execute(sql.SQL("""
        SELECT array_agg(id)
        FROM {table}
        WHERE {field_name} IS NULL or {field_name} = '/'
    """).format(
        table=sql.Identifier(table),
        field_name=sql.Identifier(field_name)
    ))
    record_ids = cr.fetchone()[0]
    if not record_ids:
        return

    for record_id in record_ids:
        new_uuid = generate_uuid_for_table(cr, table, field_name)

        cr.execute(sql.SQL("""
            UPDATE {table}
            SET {field_name}=%(uuid)s
            WHERE id=%(record_id)s
        """).format(
            table=sql.Identifier(table),
            field_name=sql.Identifier(field_name),
        ), {
            'uuid': new_uuid,
            'record_id': record_id,
        })
