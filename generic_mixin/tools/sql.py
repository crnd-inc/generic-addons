from psycopg2 import sql
from odoo import tools
from odoo.tools.sql import (
    create_column,
    column_exists,
)
from .xmlid import xmlid_to_id


def create_sql_view(cr, name, definition, materialized=False):
    """ Create SQL view with specified name and definition.
        Note, that if view already exists, it will be recreated.

        :param cr: database cursor
        :param str name: name of SQL view
        :param str definition: SQL view definition. Just a string
                               that contains SQL SELECT statement,
                               that will be used as definition of SQL View.
    """

    # pylint: disable=sql-injection
    table_kind = tools.table_kind(cr, tablename=name)
    if table_kind == 'v':
        tools.drop_view_if_exists(cr, name)
    elif table_kind == 'm':
        query = sql.SQL("""
            DROP MATERIALIZED VIEW IF EXISTS {name};
        """).format(name=sql.Identifier(name))
        if getattr(cr, 'sql_log', None):
            query = query.as_string(cr._obj)
        cr.execute(query)

    if materialized:
        query = sql.SQL("""
            CREATE MATERIALIZED VIEW {name} AS ({definition});
        """).format(name=sql.Identifier(name), definition=sql.SQL(definition))
    else:
        query = sql.SQL("""
            CREATE or REPLACE VIEW {name} AS ({definition});
        """).format(name=sql.Identifier(name), definition=sql.SQL(definition))
    if getattr(cr, 'sql_log', None):
        query = query.as_string(cr._obj)
    cr.execute(query)


def create_column_if_not_exists(cr, tablename, columnname, columntype,
                                comment=None):
    """ Create a column with the given type if it not yet exists
        and return True if column was created successfully
        otherwise return False.

        :param cr: database cursor
        :param str tablename: Name of table to add column to
        :param str columnname: Name of column to add
        :param str columntype: postgresql type of column
        :param str comment: optional comment for created column
        :return bool: True if column was created,
            False if column already exists
    """
    if not column_exists(cr, tablename, columnname):
        create_column(cr, tablename, columnname, columntype, comment)
        return True
    return False


def unlink_view(cr, xmlid):
    """ Remove view referenced by xmlid.
        This could be helpful during migrations: some times it is better
        to remove view that has unexisting columns and let odoo recreate it.

        :param cr: database cursor
        :param str xmlid: string representing external identifier (xmlid)
            of view. It must be fully qualified xmlid, that includes
            name of module.
    """
    view_id = xmlid_to_id(cr, xmlid)
    if view_id:
        cr.execute("""
            DELETE FROM ir_ui_view
            WHERE id = %(view_id)s
        """, {
            'view_id': view_id,
        })
