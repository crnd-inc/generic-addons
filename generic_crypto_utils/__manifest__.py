{
    "name": "Generic Crypto Utils",
    "version": "14.0.0.2.0",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": """Technical utils to add encryption to other addons""",
    'category': 'Technical Settings',
    'depends': [
        'base',
    ],
    'demo': [
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
