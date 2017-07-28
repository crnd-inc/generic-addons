# -*- coding: utf-8 -*-
{
    "name": "Generic Condition",
    "version": "10.0.0.0.1",
    "author": "Management and Accounting Online",
    "website": "https://maao.com.ua",
    "license": "Other proprietary",
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
