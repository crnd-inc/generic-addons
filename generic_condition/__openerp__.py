{
    "name": "Generic Condition",
    "version": "11.0.1.2.7",
    "author": "Center of Research & Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": "Create generic conditions on which you can program some logic in Odoo objects",
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
