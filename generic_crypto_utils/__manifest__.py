{
    "name": "Generic Crypto Utils",
    "version": "20.0.0.8.1",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": "LGPL-3",
    "summary": """Technical utils to add encryption to other addons""",
    'category': 'Technical Settings',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.access.csv',
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ],
    },
    'images': ['static/description/banner.png'],
}
