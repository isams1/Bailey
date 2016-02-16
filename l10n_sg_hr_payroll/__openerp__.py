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
    "name": "Singapore Payroll",
    "version": "1.3",
    "depends": ["hr_payroll", "sg_hr_employee","hr_timesheet_sheet","l10n_sg"],
    "author" :"Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "Localization",
    "description": """
Singapore Payroll Salary Rules.
============================

    -Configuration of hr_payroll for Singapore localization
    -All main contributions rules for Singapore payslip.
    * New payslip report
    * Employee Contracts
    * Allow to configure Basic / Gross / Net Salary
    * CPF for Employee and Employer salary rules
    * Employee and Employer Contribution Registers
    * Employee PaySlip
    * Allowance / Deduction
    * Integrated with Holiday Management
    * Medical Allowance, Travel Allowance, Child Allowance, ...
    
    - Payroll Advice and Report
    - Yearly Salary by Head and Yearly Salary by Employee Report
    - IR8A and IR8S esubmission txt file reports
    """,
    'data': [
       'security/group.xml',
       'security/ir.model.access.csv',
       'security/hr.employee.category.csv',
       'security/hr.salary.rule.category.csv',
       'security/hr.contribution.register.csv',
       'menu.xml',
       'salary_rule.xml',
       'security/hr.rule.input.csv',
       'payroll_extended_view.xml',
       'hr_contract_view.xml',
       'wizard/comput_confirm_payslip_wiz_view.xml',
       'views/report_payslip.xml',
       'data/account_data.xml',
    ],
    'installable': True,
    'auto_install':False,
    'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
