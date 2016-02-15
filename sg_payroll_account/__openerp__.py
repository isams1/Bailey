# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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
    "name": "Singapore Payroll Account",
    "version": "1.3",
    "depends": ['account','hr_payroll','l10n_sg', 'hr_payroll_account','l10n_sg_hr_payroll'],
    "author" :"Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "Localization",
    "description":"""
Singapore Accounting payroll data
============================
    - This module will assign account in each salary rules to make payroll accounting entries.
    """,
    "data": [
       "data/salary_rules.xml",
    ],
    "installable": True,
    "auto_install":False,
    "application":True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
