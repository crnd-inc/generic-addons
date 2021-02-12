{
    "name": "Generic Condition",
    "version": "14.0.1.8.0",
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
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/generic_condition.xml',
        'views/generic_condition_view.xml',
        'views/assets.xml',
        'wizard/test_condition_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
