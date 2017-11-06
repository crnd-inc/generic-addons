# -*- coding: utf-8 -*-
{
    "name": "Generic Condition - Test",
    "version": "10.0.0.0.1",
    "author": "Management and Accounting Online",
    "website": "https://maao.com.ua",
    "license": "Other proprietary",
    "summary": "Generic Conditions - Tests (do not install manualy)",
    'category': 'Technical Settings',
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
    'installable': True,
    'auto_install': False,
    'application': False,
}
