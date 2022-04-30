from odoo.tools.sql import (
    create_model_table,
    create_column,
    add_foreign_key,
    table_exists,

)


def migrate(cr, installed_version):
    if table_exists(cr, 'generic_team_member'):
        # There is no need to run migration in this case
        return

    create_model_table(cr, 'generic_team_member')
    create_column(cr, 'generic_team_member', 'team_id', 'integer')
    create_column(cr, 'generic_team_member', 'user_id', 'integer')
    add_foreign_key(
        cr, 'generic_team_member', 'team_id', 'generic_team', 'id', 'cascade')
    add_foreign_key(
        cr, 'generic_team_member', 'user_id', 'res_users', 'id', 'cascade')

    cr.execute("""
        INSERT INTO generic_team_member (user_id, team_id)
        (SELECT res_users_id, generic_team_id
        FROM generic_team_res_users_rel);

        DROP TABLE generic_team_res_users_rel;
        DELETE FROM ir_model_relation
        WHERE name = 'generic_team_res_users_rel';

        DELETE FROM ir_model_constraint AS imc
        WHERE model = (
               SELECT id FROM ir_model AS im WHERE im.model = 'generic.team')
          AND imc.name ILIKE 'generic_team_res_users_rel_%';
    """)
