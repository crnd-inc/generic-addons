from odoo import api, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version


@ensure_version('1.51.0')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    ResourceType = env['generic.resource.type'].with_context(active_test=False)
    for record in ResourceType.search([('code', '=', False)]):
        record.code = slugify(record.display_name, max_length=0)
