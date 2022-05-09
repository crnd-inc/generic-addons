import uuid

from psycopg2 import sql
from odoo.tools.sql import (
    create_column,
    column_exists,
)


def _generate_new_uuid(set_uuids):
    """ Generate new unique UUID, which is not yet in set_uuids
    """
    _uuid = str(uuid.uuid4())
    while _uuid in set_uuids:
        _uuid = str(uuid.uuid4())
    return _uuid


def pre_init_hook(cr):
    table = 'generic_location'
    if column_exists(cr, table, 'uuid'):
        return
    create_column(cr, table, 'uuid', 'VARCHAR')

    # pylint: disable=sql-injection
    cr.execute(
        sql.SQL("SELECT array_agg(id) FROM {}").format(sql.Identifier(table)))
    record_ids = cr.fetchone()[0]
    if not record_ids:
        return

    set_uuids = set()
    for record_id in record_ids:
        _uuid = _generate_new_uuid(set_uuids)
        set_uuids.add(_uuid)

        cr.execute(
            sql.SQL("""
                UPDATE {}
                SET uuid=%(uuid)s
                WHERE id=%(record_id)s
            """).format(sql.Identifier(table)),
            {
                'uuid': _uuid,
                'record_id': record_id,
            }
        )
