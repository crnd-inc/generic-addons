{
    'name': "Generic Rule",

    'summary': """
        Adds new top-level menu 'rules'
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Technical Settings',
    'version': '11.0.1.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    'demo': [
        'views/generic_rule_menu.xml'
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
