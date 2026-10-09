{
    'name': "Generic Mixin",

    'summary': """
    Technical module with generic mixins, that may help to build other modules
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Technical Settings',
    'version': '20.0.1.84.9',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'http_routing',
        'bus',
    ],
    'data': [
    ],
    'external_dependencies': {
        'python': ['packaging'],
    },
    #
    'assets': {
        'web.assets_backend': [
            'generic_mixin/static/src/scss/refresh_view.scss',
            'generic_mixin/static/src/js/*.js',
        ],
        'web.assets_unit_tests': [
            'generic_mixin/static/tests/**/*.test.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
