{
    'name': "Generic Rule",

    'summary': """
        Adds new top-level menu 'rules'
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Technical Settings',
    'version': '17.0.1.9.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    'data': [
        'views/generic_rule_menu.xml'
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
