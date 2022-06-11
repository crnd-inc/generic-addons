import logging

from odoo.tools.sql import (
    column_exists,
)
from odoo.addons.generic_mixin.tools.uuid import (
    auto_generate_uuids,
    create_uuid_field,
)

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    if column_exists(cr, 'generic_location', 'uuid'):
        _logger.warning(
            "generic_location: uuid column already exists, "
            "no need to run pre-init hook")
        return

    create_uuid_field(cr, 'generic_location', 'uuid')

    auto_generate_uuids(cr, 'generic_location', 'uuid')
