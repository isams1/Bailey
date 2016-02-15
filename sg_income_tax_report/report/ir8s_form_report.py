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

from openerp.report import report_sxw
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from time import gmtime, strftime
from openerp import tools

class ppd_ir8s_form(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(ppd_ir8s_form,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                'get_data' : self.get_data
        })

    def get_data(self, form):
        vals = []
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        hr_contract_income_tax_obj = self.pool.get('hr.contract.income.tax')
        if form.get('year_id')[1]:
            start_date = '%s-01-01' % tools.ustr(int(form.get('year_id')[1]) - 1)
            end_date = '%s-12-31' % tools.ustr(int(form.get('year_id')[1]) - 1)
            start_date = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)
        contract_ids = contract_obj.search(self.cr, self.uid, [('employee_id','in',form.get('employee_ids'))])
        for contract in contract_obj.browse(self.cr, self.uid, contract_ids):
            contract_income_tax_ids = hr_contract_income_tax_obj.search(self.cr, self.uid, [('contract_id','=',contract.id),('year_id','=',form.get('year_id')[0])])
            if contract_income_tax_ids:
                res = {}
                birthday = cessation_date = ''
                if contract.employee_id.birthday:
                    birthday = datetime.datetime.strptime(contract.employee_id.birthday, DEFAULT_SERVER_DATE_FORMAT)
                    birthday = birthday.strftime('%d/%m/%Y')
                if contract.employee_id.cessation_date:
                    cessation_date = datetime.datetime.strptime(contract.employee_id.cessation_date, DEFAULT_SERVER_DATE_FORMAT)
                    cessation_date = cessation_date.strftime('%d/%m/%Y')
                
                emp_id = employee_obj.search(self.cr, self.uid, [('user_id', '=', int(form.get('payroll_user')))])
                emp_designation = ''
                user_obj = self.pool.get('res.users')
                payroll_admin_user_name = user_obj.browse(self.cr, self.uid, int(form.get('payroll_user'))).name
                signature = user_obj.browse(self.cr, self.uid, int(form.get('payroll_user'))).signature
                for emp in employee_obj.browse(self.cr, self.uid, emp_id):
                    emp_designation = emp.job_id.name
                
                res['emp_designation'] = emp_designation
                res['signature'] = signature
                res['payroll_admin_user_name'] = payroll_admin_user_name
                
                for emp in hr_contract_income_tax_obj.browse(self.cr, self.uid, [contract_income_tax_ids[0]]):
                    payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', contract.employee_id.id), ('state', 'in', ['draft', 'done', 'verify'])])
                    jan_gross_amt = feb_gross_amt = march_gross_amt = apr_gross_amt = may_gross_amt = june_gross_amt = july_gross_amt = aug_gross_amt = sept_gross_amt = oct_gross_amt = nov_gross_amt = dec_gross_amt = 0
                    jan_empoyer_amt = feb_empoyer_amt = march_empoyer_amt = apr_empoyer_amt = may_empoyer_amt = june_empoyer_amt = july_empoyer_amt = aug_empoyer_amt = sept_empoyer_amt = oct_empoyer_amt = nov_empoyer_amt = dec_empoyer_amt = 0
                    jan_empoyee_amt = feb_empoyee_amt = march_empoyee_amt = apr_empoyee_amt = may_empoyee_amt = june_empoyee_amt = july_empoyee_amt = aug_empoyee_amt = sept_empoyee_amt = oct_empoyee_amt = nov_empoyee_amt = dec_empoyee_amt = 0
                    tot_gross_amt = tot_empoyee_amt = tot_empoyer_amt = 0
                    for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                        payslip_month = ''
                        payslip_month = datetime.datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT)
                        payslip_month = payslip_month.strftime('%m')
                        gross_amt = empoyer_amt = empoyee_amt = 0
                        for line in payslip.line_ids:
                            if line.code == 'NET':
                                gross_amt = line.amount
                            if line.category_id.code == 'CAT_CPF_EMPLOYER':
                                empoyer_amt += line.amount
                            if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                                empoyee_amt += line.amount
                        tot_gross_amt += gross_amt
                        tot_empoyer_amt += empoyer_amt
                        tot_empoyee_amt += empoyee_amt
                        
                        if payslip_month == '01':
                            jan_gross_amt = gross_amt
                            jan_empoyer_amt = empoyer_amt
                            jan_empoyee_amt = empoyee_amt
                        if payslip_month == '02':
                            feb_gross_amt = gross_amt
                            feb_empoyer_amt = empoyer_amt
                            feb_empoyee_amt = empoyee_amt
                        if payslip_month == '03':
                            march_gross_amt = gross_amt
                            march_empoyer_amt = empoyer_amt
                            march_empoyee_amt = empoyee_amt
                        if payslip_month == '04':
                            apr_gross_amt = gross_amt
                            apr_empoyer_amt = empoyer_amt
                            apr_empoyee_amt = empoyee_amt
                        if payslip_month == '05':
                            may_gross_amt = gross_amt
                            may_empoyer_amt = empoyer_amt
                            may_empoyee_amt = empoyee_amt
                        if payslip_month == '06':
                            june_gross_amt = gross_amt
                            june_empoyer_amt = empoyer_amt
                            june_empoyee_amt = empoyee_amt
                        if payslip_month == '07':
                            july_gross_amt = gross_amt
                            july_empoyer_amt = empoyer_amt
                            july_empoyee_amt = empoyee_amt
                        if payslip_month == '08':
                            aug_gross_amt = gross_amt
                            aug_empoyer_amt = empoyer_amt
                            aug_empoyee_amt = empoyee_amt
                        if payslip_month == '09':
                            sept_gross_amt = gross_amt
                            sept_empoyer_amt = empoyer_amt
                            sept_empoyee_amt = empoyee_amt
                        if payslip_month == '10':
                            oct_gross_amt = gross_amt
                            oct_empoyer_amt = empoyer_amt
                            oct_empoyee_amt = empoyee_amt
                        if payslip_month == '11':
                            nov_gross_amt = gross_amt
                            nov_empoyer_amt = empoyer_amt
                            nov_empoyee_amt = empoyee_amt
                        if payslip_month == '12':
                            dec_gross_amt = gross_amt
                            dec_empoyer_amt = empoyer_amt
                            dec_empoyee_amt = empoyee_amt
                    res['emp_name'] = contract.employee_id.name
                    res['identification_id'] = contract.employee_id.identification_id
                    res['work_phone'] = contract.employee_id.work_phone
                    res['birthday'] = birthday
                    res['cessation_date'] = cessation_date
                    res['jan_gross_amt'] = jan_gross_amt
                    res['feb_gross_amt'] = feb_gross_amt
                    res['march_gross_amt'] = march_gross_amt
                    res['apr_gross_amt'] = apr_gross_amt
                    res['may_gross_amt'] = may_gross_amt
                    res['june_gross_amt'] = june_gross_amt
                    res['july_gross_amt'] = july_gross_amt
                    res['aug_gross_amt'] = aug_gross_amt
                    res['sept_gross_amt'] = sept_gross_amt
                    res['oct_gross_amt'] = oct_gross_amt
                    res['nov_gross_amt'] = nov_gross_amt
                    res['dec_gross_amt'] = dec_gross_amt
                    
                    res['jan_empoyee_amt'] = jan_empoyee_amt
                    res['feb_empoyee_amt'] = feb_empoyee_amt
                    res['march_empoyee_amt'] = march_empoyee_amt
                    res['apr_empoyee_amt'] = apr_empoyee_amt
                    res['may_empoyee_amt'] = may_empoyee_amt
                    res['june_empoyee_amt'] = june_empoyee_amt
                    res['july_empoyee_amt'] = july_empoyee_amt
                    res['aug_empoyee_amt'] = aug_empoyee_amt
                    res['sept_empoyee_amt'] = sept_empoyee_amt
                    res['oct_empoyee_amt'] = oct_empoyee_amt
                    res['nov_empoyee_amt'] = nov_empoyee_amt
                    res['dec_empoyee_amt'] = dec_empoyee_amt
                    
                    
                    res['jan_empoyer_amt'] = jan_empoyer_amt
                    res['feb_empoyer_amt'] = feb_empoyer_amt
                    res['march_empoyer_amt'] = march_empoyer_amt
                    res['apr_empoyer_amt'] = apr_empoyer_amt
                    res['may_empoyer_amt'] = may_empoyer_amt
                    res['june_empoyer_amt'] = june_empoyer_amt
                    res['july_empoyer_amt'] = july_empoyer_amt
                    res['aug_empoyer_amt'] = aug_empoyer_amt
                    res['sept_empoyer_amt'] = sept_empoyer_amt
                    res['oct_empoyer_amt'] = oct_empoyer_amt
                    res['nov_empoyer_amt'] = nov_empoyer_amt
                    res['dec_empoyer_amt'] = dec_empoyer_amt
                    
                    res['eyer_contibution'] = emp.eyer_contibution
                    res['eyee_contibution'] = emp.eyee_contibution
                    
                    res['additional_wage'] = emp.additional_wage
                    res['add_wage_pay_date'] = emp.add_wage_pay_date
                    res['refund_eyers_contribution'] = emp.refund_eyers_contribution
                    res['refund_eyees_contribution'] = emp.refund_eyees_contribution
                    res['refund_eyers_date'] = emp.refund_eyers_date
                    res['refund_eyees_date'] = emp.refund_eyees_date
                    res['refund_eyers_interest_contribution'] = emp.refund_eyers_interest_contribution
                    res['refund_eyees_interest_contribution'] = emp.refund_eyees_interest_contribution
                    res['date_today'] = datetime.date.today()
                vals.append(res)
        return vals

report_sxw.report_sxw('report.ppd_ir8s_form_report','hr.payslip','addons/sg_income_tax_report/report/ir8s_form_report_tmpl.rml',parser=ppd_ir8s_form)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: