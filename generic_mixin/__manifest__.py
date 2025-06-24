{
    'name': "Generic Mixin",

    'summary': """
    Technical module with generic mixins, that may help to build other modules
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Technical Settings',
    'version': '18.0.1.82.3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'http_routing',
        'bus',
    ],
    'data': [
    ],
    #
    'assets': {
        # Disabled refresher during forwardport on v.17.0
        # 'web.assets_backend': [
        #     'generic_mixin/static/src/scss/refresh_view.scss',
        #     'generic_mixin/static/src/js/*.js',
        # ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
