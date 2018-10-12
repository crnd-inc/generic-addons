{
    'name': "Generic Tag (Product) (Experimental) ",

    'summary': """
        Generic tag integration with product addon
    """,

    'author': "Center of Research & Development",
    'website': "https://crnd.pro",

    'category': 'Generic Tags',
    'version': '11.0.1.0.2',

    "depends": [
        "generic_tag",
        "product",
    ],

    "data": [
        'data/generic_tag_model.xml',
        'views/product.xml',
        'views/generic_tag_product.xml'
    ],
    "installable": True,
    "auto_install": False,
    'license': 'LGPL-3',
}
