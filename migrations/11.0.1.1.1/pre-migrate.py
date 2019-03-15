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
        select id from ir_model
        where name='generic.team.member';
    """)
    model_id = cr.fetchone()[0]

    if not model_id:
        cr.execute("""
            insert into ir_model (name, model)
            values ('generic.team.member', 'generic.team.member')
            returning id;
        """)
        model_id = cr.fetchone()[0]

    cr.execute("""
        select count(*)
        from ir_model_access
        where name like 'generic_team_member';
    """)
    cn = cr.fetchone()[0]

    if cn == 0:
        cr.execute("""
            insert into ir_model_access (name, model_id)
            values
            ('generic_team_member_user_implicit', %(model_id)s),
            ('generic_team_member_user', %(model_id)s),
            ('generic_team_member_manager', %(model_id)s);
        """, {'model_id': model_id})

    cr.execute("""
        select count(*) from ir_model_data
        where name='model_generic_team_member' and module='generic_team';
    """)
    cn = cr.fetchone()[0]

    if cn == 0:
        cr.execute("""
            insert into ir_model_data (name, module, model, res_id)
            values ('model_generic_team_member', 'generic_team', 'ir.model', %(model_id)s);
        """, {'model_id': model_id})
