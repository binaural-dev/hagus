# -*- coding: utf-8 -*-

{
    'name': 'Modificaciones Hagus',
    'version': '14.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': """
        'Modificaciones Hagus
    """,
    'description': """Personalizaciones Hagus""",
    'author': 'Binaural',
    'company': 'Binaural',
    'maintainer': 'Binaural',
    'website': 'https://binauraldev.com/',
    'depends': ['mrp','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/troquel.xml',
        'views/orientation.xml',
        'views/finish_types.xml',
        'views/clisse.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}