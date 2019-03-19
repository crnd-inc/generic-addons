def migrate(cr, installed_version):
    cr.execute("""
        ALTER TABLE IF EXISTS generic_team_res_users_rel
            RENAME TO generic_team_member;
        ALTER TABLE IF EXISTS generic_team_member
            RENAME COLUMN generic_team_id
               TO team_id;
        ALTER TABLE IF EXISTS generic_team_member
            RENAME COLUMN res_users_id
               TO user_id;
    """)

    # cr.execute("""
        # SELECT id FROM ir_model
        # WHERE name='generic.team.member';
    # """)

    # if cr.rowcount == 0:
        # cr.execute("""
            # INSERT INTO ir_model (name, model)
            # VALUES ('generic.team.member', 'generic.team.member')
            # RETURNING ID;
        # """)
        # model_id = cr.fetchone()[0]
    # else:
        # model_id = cr.fetchone()[0]

    # cr.execute("""
        # SELECT * FROM ir_model_data
        # WHERE name='model_generic_team_member' AND module='generic_team';
    # """)
    # cn = cr.rowcount

    # if cn == 0:
        # cr.execute("""
            # INSERT INTO ir_model_data (name, module, model, res_id)
            # VALUES (
            # 'model_generic_team_member',
            # 'generic_team', 'ir.model', %(model_id)s);
        # """, {'model_id': model_id})
