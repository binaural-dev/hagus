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
    'depends': [
        'mrp',
        'sale_management',
        'crm','purchase',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/orientation.xml',
        'data/product_category.xml',
        # 'data/product.xml',
        'data/sequence.xml',
        'views/troquel.xml',
        'views/res_partner.xml',
        'views/orientation.xml',
        'views/finish_types.xml',
        'views/clisse.xml',
        'views/sequence_views.xml',
        'views/res_company.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/mrp_production.xml',
        'views/crm_lead.xml',
        'views/purchase.xml',
        'report/hagus_clisse_templates.xml',
        'report/hagus_clisse_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
