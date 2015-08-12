# -*- coding: utf-8 -*-
{
    'name' : "Streamline AME Modules",
    'version' : "1.0",
    'author' : "Streamline Pte Ltd",
    'description' : '''
        All modules of AME client need to put in here.
    ''',
    'category' : "Streamline Pte Ltd - AME",
    'depends' : ['web','report','account', 'product', 'warehouse_extended'],
    'website': 'http://streamline.sg/',
    'js': ['static/src/js/datetimepicker.js'],
    'data' : [
        'reports/account/wizard/invoice_summary_view.xml',
        'reports/account/wizard/stock_report_view.xml',
        'reports/account/views/report_invoice_summary.xml',
        'reports/account/views/report_stock_report.xml',
        'reports/sale/views/report_saleorder.xml',
        'reports/stock/wizard/product_aging_view.xml',
        'reports/stock/views/report_product_aging.xml',
        'reports/stock/wizard/item_consumption_by_site_view.xml',
        'reports/stock/views/report_item_consumption_by_site.xml',
        'reports/menu.xml',
        'products/data/product_sequence.xml',
        'products/views/product_view.xml',
        'sales/views/sale_order.xml',
        'view/templates.xml',
    ],
    'pre_init_hook': 'update_null_and_slash_codes',
    'demo' : [],
    'installable': True,
    'auto_install': False
}