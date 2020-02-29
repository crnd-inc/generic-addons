from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for record in env['generic.tag.model'].search([]):
        cr.execute("""
            INSERT INTO ir_act_window
                   (name, res_model, binding_type,
                    view_mode, target, context,
                    type, binding_model_id)
            VALUES ('Manage Tags', 'generic.tag.wizard.manage.tags', 'action',
                    'form', 'new', %(context)s,
                    'ir.actions.act_window', %(binding_model_id)s)
            RETURNING id;
        """, {
            'binding_model_id': record.res_model_id.id,
            'context': (
                "{"
                "'manage_tags_model': active_model,"
                "'manage_tags_object_ids': active_ids,"
                "}"),
        })
        record.act_manage_tags_id = cr.fetchone()[0]
