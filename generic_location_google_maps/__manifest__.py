{
    'name': "Generic Location (Google Maps)",

    'summary': """
        Generic Location (View locations on google maps)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.0.10',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_geolocalize',
        'web_google_maps',
    ],

    # always loaded
    'data': [
        'views/generic_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'uninstall_hook': 'uninstall_hook',
}
