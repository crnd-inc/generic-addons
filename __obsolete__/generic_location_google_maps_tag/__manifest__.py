{
    'name': "Generic Location (Google Maps + Tags) [Obsolete]",

    'summary': (
        "The functionality of this module was merged "
        "into the 'generic_location_google_maps' module, "
        "thus this module could be safely removed."),

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.3.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location_google_maps',
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'AGPL-3',
    'tags': ['obsolete'],
}
