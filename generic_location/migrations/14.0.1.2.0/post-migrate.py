from odoo import api, SUPERUSER_ID
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version


@ensure_version('1.2.0')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['generic.location']._parent_store_compute()
