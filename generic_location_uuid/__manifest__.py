{
    'name': "Generic Location (UUID)",

    'summary': "Generic Location (Add UUID to generic locations)",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '16.0.1.4.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': False,
    'application': False,
    'license': 'LGPL-3',
}
