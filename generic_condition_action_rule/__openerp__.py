# -*- coding: utf-8 -*-
{
    "name": "Generic Condition - Action Rules",
    "version": "9.0.0.0.1",
    "author": "Management and Accounting Online",
    "website": "https://maao.com.ua",
    "license": "Other proprietary",
    "summary": "Generic Conditions (Integration with Action Rules)",
    'category': 'Technical Settings',
    'depends': [
        'generic_condition',
        'base_action_rule',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'data': [
        'views/base_action_rule_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
