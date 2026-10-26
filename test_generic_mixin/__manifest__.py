{
    'name': "Generic Mixin (Tests)",
    'summary': (
        'Technical module that have to be used to test Generic Mixin '
        'module'
    ),
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Hidden',
    'version': '20.0.0.25.7',
    'depends': [
        'generic_mixin',
        'calendar',
    ],
    'data': [
        'views/test_refresh_view.xml',
        'views/test_contact_mixin.xml',
        'security/ir.access.csv',
    ],
    'demo': [
        'demo/test_track_changes.xml',
        'demo/test_noupdate_on_write.xml',
        'demo/ir_sequence.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
}
