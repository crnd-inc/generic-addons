{
    'name': "Generic team",

    'summary': """
        With this module you can create teams and add
        users to them, which allows you to perform group
        actions (such as assigning a responsible team
        instead of one person) while working with Odoo applications.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Team',
    'version': '13.0.1.13.0',

    "depends": [
        'base',
        'mail',
        'base_field_m2m_view',
        'generic_mixin',
    ],

    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/generic_team_menu.xml',
        'views/generic_team.xml',
        'views/generic_team_member_view.xml',
        'views/res_users.xml',
        'views/templates.xml',
    ],

    "demo": [
        'demo/generic_team_demo.xml'
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
    'license': 'LGPL-3',
}
