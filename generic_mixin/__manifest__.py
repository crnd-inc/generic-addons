{
    'name': "Generic Mixin",

    'summary': """
    Technical module with generic mixins, that may help to build other modules
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Technical Settings',
    'version': '16.0.1.81.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'http_routing',
        'bus',
    ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'generic_mixin/static/src/scss/refresh_view.scss',
            'generic_mixin/static/src/js/*.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
