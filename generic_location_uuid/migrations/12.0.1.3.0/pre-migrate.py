import logging

from odoo.tools.sql import column_exists
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    Location = env['generic.location'].with_context(active_test=False)

    _logger.warning('\n\n Vals PRE MIGRATE\n %s\n\n',
                    (Location.search([]).read(['name', 'uuid'])))
    cr.execute("""
        SELECT id, uuid
        FROM generic_location
    """)
    _logger.warning('\n\n Vals PRE MIGRATE FETCHALL\n %s\n\n',
                    (cr.fetchall()))

    if column_exists(cr, 'generic_location', 'uuid'):
        _logger.warning(
            "GENERIC_LOCATION: UUID COLUMN ALREADY EXISTS, "
            "NEED TO CHECK")
        return

    _logger.warning("Running PRE MIGRATE for geneirc_location_uuid...")
