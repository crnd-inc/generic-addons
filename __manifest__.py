{
    'name': "Generic team",

    'summary': """
        Generic team.
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Team',
    'version': '11.0.1.0.5',

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

    "installable": True,
    "application": False,
    'license': 'Other proprietary',
}
