from psycopg2 import sql
from odoo import tools


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
