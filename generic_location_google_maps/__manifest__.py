{
    'name': "Generic Location (Google Maps)",

    'summary': """
        Generic Location (View locations on google maps)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '13.0.1.2.0',

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
    'installable': False,
    'application': False,
    'license': 'AGPL-3',
    'uninstall_hook': 'uninstall_hook',
}
