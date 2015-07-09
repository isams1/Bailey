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
        'reports/account/views/report_invoice_summary.xml',
    ],
    'demo' : [],
    'installable': True,
    'auto_install': False
}