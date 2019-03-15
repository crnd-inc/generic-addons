def migrate(cr, installed_version):
    cr.execute("""
        CREATE TABLE IF NOT EXISTS generic_team_member (
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL);

        INSERT INTO generic_team_member (user_id, team_id)
        (SELECT res_users_id, generic_team_id
        FROM generic_team_res_users_rel);
    """)

    cr.execute("""
        SELECT id FROM ir_model
        WHERE name='generic.team.member';
    """)

    if cr.rowcount == 0:
        cr.execute("""
            INSERT INTO ir_model (name, model)
            VALUES ('generic.team.member', 'generic.team.member')
            RETURNING ID;
        """)
        model_id = cr.fetchone()[0]
    else:
        model_id = cr.fetchone()[0]

    cr.execute("""
        SELECT *
        FROM ir_model_access
        WHERE name='generic_team_member';
    """)
    cn = cr.rowcount

    if cn == 0:
        cr.execute("""
            INSERT INTO ir_model_access (name, model_id)
            VALUES
            ('generic_team_member_user_implicit', %(model_id)s),
            ('generic_team_member_user', %(model_id)s),
            ('generic_team_member_manager', %(model_id)s);
        """, {'model_id': model_id})

    cr.execute("""
        SELECT * FROM ir_model_data
        WHERE name='model_generic_team_member' AND module='generic_team';
    """)
    cn = cr.rowcount

    if cn == 0:
        cr.execute("""
            INSERT INTO ir_model_data (name, module, model, res_id)
            VALUES (
            'model_generic_team_member',
            'generic_team', 'ir.model', %(model_id)s);
        """, {'model_id': model_id})
