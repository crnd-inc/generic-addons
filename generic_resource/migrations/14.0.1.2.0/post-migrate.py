from odoo import api, SUPERUSER_ID
from odoo.addons.generic_mixin.tools.migration_utils import ensure_version


@ensure_version('1.2.0')
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for resource_type in env['generic.resource.type'].search([]):
        cr.execute("""
            INSERT INTO ir_act_window
                   (name, multi, res_model, binding_type,
                    src_model, view_mode, target, context,
                    view_type, domain, type, binding_model_id)
            VALUES (%(name)s, %(multi)s, %(res_model)s, %(binding_type)s,
                    %(src_model)s, %(view_mode)s, %(target)s, %(context)s,
                    %(view_type)s, %(domain)s, %(type)s, %(binding_model_id)s)
            RETURNING id;
        """, {
            'name': 'Related Resources',
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'binding_model_id': resource_type.model_id.id,
            'multi': True,
            'res_model': 'generic.resource',
            'src_model': resource_type.model,
            'view_mode': 'tree,form',
            'target': 'current',
            'view_type': 'form',
            'domain': (
                "[('res_id', 'in', active_ids),"
                "('res_model', '=', active_model)]"),
            'context': '{}',

        })
        action_id = cr.fetchone()[0]
        resource_type.resource_related_res_action_id = action_id
