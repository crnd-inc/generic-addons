{
    'name': "Generic Location (Google Maps + Tags)",

    'summary': """
        Generic Location (Techinical addon that
        shows location tags on map view)""",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '13.0.1.2.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_google_maps',
        'generic_location_tag',
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
    'auto_install': True,
    'application': False,
    'license': 'AGPL-3',
}
