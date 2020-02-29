{
    "name": "Generic Condition - Test",
    "version": "12.0.1.4.0",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": "Generic Conditions - Tests (do not install manualy)",
    'category': 'Hidden',
    'depends': [
        'generic_condition',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/test_model_demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
