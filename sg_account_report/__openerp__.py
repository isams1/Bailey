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
    "name" : "Singapore - Accounting",
    "version" : "1.0",
    "author" : "Serpent Consulting Services Pvt. Ltd.",
    'category': 'Localization/Account Reports',
    "website" : "http://www.serpentcs.com",
    "description": """
Singapore Accounting: Account Report.
====================================

* Trial Balance
* Balnce sheet
* Profit & Loss
* Partner Aeging report

""",
    'depends': ['account', 'account_chart'],
    'demo': [],
    'data': [
        'security/security.xml',
        'report.xml',
        'wizard.xml',
        'account_view.xml',
        'company_view.xml',
        'account_financial_report_view.xml',
        'report/financial_report_view.xml',
        'wizard/partner_aged_report.xml'
#        'report_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
