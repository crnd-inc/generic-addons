{
    "name": "Generic Condition",
    "version": "11.0.1.0.0",
    "author": "Center of Research & Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": "Generic Conditions",
    'category': 'Technical Settings',
    'depends': [
        'web',
        'generic_m2o',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/generic_condition_view.xml',
        'views/assets.xml',
        'wizard/test_condition_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
