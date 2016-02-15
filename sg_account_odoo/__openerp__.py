# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2012 OpenERP SA (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Singapore - Accounting for odoo",
    "version" : "1.0",
    "author" : "Serpent Consulting Services Pvt. Ltd.",
    'category': 'Localization/Account Reports',
    "website" : "http://www.serpentcs.com",
    "description": """
Singapore Accounting: QWeb reports of Account.
==============================================

Singapore accounting IRAS compliance report for

* Genertion of GST form 5 and GST form 7 reports as per official l10n_sg COA.

""",
    'depends': ['l10n_sg', 'sale', 'purchase', 'stock'],
    'demo': [],
    'data': [
             'partner_view.xml',
             'wizard/e_tax_wiz_view.xml',
             'wizard/gstreturn_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
