from odoo.addons.generic_mixin.tools.migration_utils import (
    ensure_version,
    migrate_xmlids_to_module,
    cleanup_module_data,
)


@ensure_version('1.4.0')
def migrate(cr, installed_version):
    migrate_xmlids_to_module(
        cr,
        src_module='generic_location_google_maps_tag',
        dst_module='generic_location_google_maps',
        models=[
            'ir.model.fields',
            'ir.model.constraint',
            'ir.model.relation',
            'ir.ui.menu',
            'ir.model.access',
            'ir.actions.act_window',
        ],
        cleanup=True,
    )

    # Cleanup module data
    cleanup_module_data(cr, 'generic_location_google_maps_tag')
