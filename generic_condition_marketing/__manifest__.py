{
    "name": "Generic Condition - Marketing",
    "version": "12.0.0.0.11",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
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
    'images': ['static/description/banner.png'],
    'installable': False,
    'auto_install': True,
}
