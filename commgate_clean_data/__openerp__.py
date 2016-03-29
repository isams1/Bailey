# -*- encoding: utf-8 -*-
{
    'name' : 'Commgate Clean Data',
    'version' : '0.1',
    'author' : 'Commgate - Development Team',
    'category' : 'Commgate Pte Ltd - MB',
    'description': """
        Clean database
        """,
    'depends': ['base', 'sale', 'account'],
    'data': [
        "cleanup_view.xml"
        ],
    'installable': True,
    'auto_install': False
}
