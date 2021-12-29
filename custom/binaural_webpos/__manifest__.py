# -*- coding: utf-8 -*-
{
    'name': "binaural_webpos",

    'summary': """
        Modulo para integracion de webpos para facturacion electronica con panama""",

    'description': """
        Este modulo permite sincronizar documentos fiscales y no fiscales al servicio webpos de panama,
        facturas, notas de credito, notas de debito y documentos no fiscales
    """,

    'author': "Binaural C.A.",
    'website': "http://www.binauraldev.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_edi','account_debit_note'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_webpos_data.xml',
        'data/facturx_webpos_templates.xml',
        'views/views.xml',
        'views/templates.xml',        
        'views/account_tax_inherit.xml',
        'views/account_move_inherit.xml',
        'views/account_payment_inherit.xml',
        'views/tipo_pago_webpos.xml',
        'views/res_users_inherit.xml',
        'views/fiscal_machine.xml'        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
