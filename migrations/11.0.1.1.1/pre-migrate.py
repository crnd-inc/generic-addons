def migrate(cr, installed_version):
    cr.execute("""
        CREATE TABLE IF NOT EXISTS generic_team_member (
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL);

        INSERT INTO generic_team_member (user_id, team_id)
        VALUES SELECT res_users_id, generic_team_id
        FROM generic_team_res_users_rel;
    """)
