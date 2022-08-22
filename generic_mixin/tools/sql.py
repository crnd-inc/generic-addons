from psycopg2 import sql
from odoo import tools
from odoo.tools.sql import (
    create_column,
    column_exists,
)


def create_sql_view(cr, name, definition):
    """ Create SQL view with specified name and definition.
        Note, that if view already exists, it will be recreated.

        :param cr: database cursor
        :param str name: name of SQL view
        :param str definition: SQL view definition. Just a string
                               that contains SQL SELECT statement,
                               that will be used as definition of SQL View.
    """

    # pylint: disable=sql-injection
    tools.drop_view_if_exists(cr, name)
    query = sql.SQL("""
        CREATE or REPLACE VIEW {name} AS ({definition});
    """).format(name=sql.Identifier(name), definition=sql.SQL(definition))
    if getattr(cr, 'sql_log', None):
        query = query.as_string(cr._obj)
    cr.execute(query)


def create_column_if_not_exists(
        cr, tablename, columnname, columntype, comment=None):
    """ Create a column with the given type if not exists
        and return True otherwise return False.
    """
    if not column_exists(cr, tablename, columnname):
        create_column(cr, tablename, columnname, columntype, comment)
        return True
    return False
