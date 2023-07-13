{
    'name': "Tests Generic Resource (Search Tests)",
    'summary': (
        "Technical module that have to be used to test "
        "Generic Resource search cases "),
    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Hidden',
    'version': '12.0.0.1.0',
    'depends': [
        'generic_resource',
        'generic_m2o',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/test_generic_resource_name_search.xml'
    ],
    'demo': [
        'demo/demo_resource.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
