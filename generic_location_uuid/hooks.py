import uuid
import logging

from odoo.tools.sql import (
    create_column,
    column_exists,
)

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.warning('\n\n Vals PRE_INIT_HOOK\n %s\n\n', ())
    if column_exists(cr, 'generic_location', 'uuid'):
        _logger.warning(
            "generic_location: uuid column already exists, "
            "no need to run pre-init hook")
        return

    _logger.warning("Running pre_init_hook for geneirc_location_uuid...")
    create_column(cr, 'generic_location', 'uuid', 'VARCHAR')

    cr.execute("SELECT array_agg(id) FROM generic_location")
    record_ids = cr.fetchone()[0]
    if not record_ids:
        return

    for record_id in record_ids:
        new_uuid_ok = False
        while not new_uuid_ok:
            new_uuid = str(uuid.uuid4())

            # Ensure that uuid is unique
            cr.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM generic_location
                    WHERE uuid = %(uuid)s
                )
            """, {'uuid': new_uuid})
            if not cr.fetchone()[0]:
                new_uuid_ok = True

        cr.execute("""
            UPDATE generic_location
            SET uuid=%(uuid)s
            WHERE id=%(record_id)s
        """, {
            'uuid': new_uuid,
            'record_id': record_id,
            })
