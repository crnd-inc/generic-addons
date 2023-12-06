{
    'name': "Generic Location: Map",

    'summary': "Display locations on map view.",

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '13.0.1.13.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location',
        'generic_location_geolocalize',
        'crnd_web_map_view',
        'crnd_web_widget_select_geolocation',
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
}
