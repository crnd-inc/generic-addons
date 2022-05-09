from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    GenericLocation = env['generic.location'].with_context(active_test=False)
    records = GenericLocation.search([
        '|', ('uuid', '=', False), ('uuid', '=', '/'),
    ])
    for record in records:
        record.uuid = record._generic_mixin_uuid__generate_new()
