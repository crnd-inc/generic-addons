{
    'name': "Generic Tag (Product) (Experimental) ",

    'summary': """
        Generic tag integration with product addon
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '13.0.1.2.0',

    "depends": [
        "generic_tag",
        "product",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/product.xml',
        'views/generic_tag_product.xml'
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "auto_install": False,
    'license': 'LGPL-3',
}
