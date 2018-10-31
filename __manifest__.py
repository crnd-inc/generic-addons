{
    'name': "Generic team",

    'summary': """
        With this module you can create teams and add
        users to them, which allows you to perform group
        actions (such as assigning a responsible team
        instead of one person) while working with Odoo applications.
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Team',
    'version': '11.0.1.0.7',

    "depends": [
        'base',
        'mail',
    ],

    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/generic_team_menu.xml',
        'views/generic_team.xml',
        'views/templates.xml',
    ],

    "demo": [
        'demo/generic_team_demo.xml'
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
    'license': 'OPL-1',
}
