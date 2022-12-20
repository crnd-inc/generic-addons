{
    'name': "Generic Location (Address) [Obsolete]",

    'summary': (
        "The functionality of this module was merged "
        "into the 'generic_location' module, "
        "thus this module could be safely removed."),

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Location',
    'version': '12.0.1.6.0',

    # any module necessary for this one to work correctly
    'depends': [
        'generic_location',
    ],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'tags': ['obsolete'],
}
