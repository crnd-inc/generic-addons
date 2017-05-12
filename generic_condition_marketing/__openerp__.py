# -*- coding: utf-8 -*-
{
    "name": "Generic Condition - Marketing",
    "version": "9.0.0.0.1",
    "author": "Management and Accounting Online",
    "website": "https://maao.com.ua",
    "license": "Other proprietary",
    "summary": "Generic Conditions (Integration with marketing campaigns)",
    'category': 'Marketing',
    'depends': [
        'generic_condition',
        'marketing_campaign',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/marketing_campaign_view.xml',
        # 'wizard/test_condition_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
