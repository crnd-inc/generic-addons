{
    "name": "Generic Condition",
    "version": "17.0.1.22.2",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": """
        Create generic conditions on which you
        can program some logic in Odoo objects""",
    'category': 'Technical Settings',
    'depends': [
        'web',
        'mail',
        'generic_m2o',
        'generic_rule',
        'generic_mixin',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'data': [
        'data/generic_condition.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/generic_condition_view.xml',
        'wizard/test_condition_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/generic_condition/static/src/css/style.css',

            '/generic_condition/static/src/js/fake_selection.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
