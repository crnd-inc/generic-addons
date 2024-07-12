{
    'name': "Generic Location: Map",

    'summary': "Display locations on map view.",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '17.0.1.9.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location',
        'crnd_web_map_view',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    'installable': False,
    'application': False,
    'license': 'LGPL-3',
}
