# -*- coding: utf-8 -*-
{
    'name' : "Streamline AME Modules",
    'version' : "1.0",
    'author' : "Streamline Pte Ltd",
    'description' : '''
        All modules of AME client need to put in here.
    ''',
    'category' : "Streamline Pte Ltd - AME",
    'depends' : ['report','account', 'product', 'warehouse_extended'],
    'website': 'http://streamline.sg/',
    'data' : [
        'reports/account/wizard/invoice_summary_view.xml',
        'reports/account/wizard/stock_report_view.xml',
        'reports/account/views/report_invoice_summary.xml',
        'reports/account/wizard/menu.xml',
        'products/data/product_sequence.xml',
        'products/views/product_view.xml',
    ],
    'pre_init_hook': 'update_null_and_slash_codes',
    'demo' : [],
    'installable': True,
    'auto_install': False
}