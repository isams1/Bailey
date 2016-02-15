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
from openerp.osv import osv
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp import tools

class ppd_ir8a_form(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(ppd_ir8a_form,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
            'get_data' : self.get_data
        })

    def get_data(self, form):
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        user_pool = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        resource_pool = self.pool.get('resource.resource')
        hr_contract_income_tax_obj = self.pool.get('hr.contract.income.tax')
        start_date = end_date = prev_yr_start_date = prev_yr_end_date = False
        if form['year_id'][1]:
            fiscal_start_date = '%s0101' % tools.ustr(int(form['year_id'][1]) - 1)
            fiscal_end_date = '%s1231' % tools.ustr(int(form['year_id'][1]) - 1)
            start_date = '%s-01-01' % tools.ustr(int(form['year_id'][1]) - 1)
            end_date = '%s-12-31' % tools.ustr(int(form['year_id'][1]) - 1)
            prev_yr_start_date = '%s-01-01' % tools.ustr(int(form['year_id'][1]) - 2)
            prev_yr_end_date = '%s-12-31' % tools.ustr(int(form['year_id'][1]) - 2)
            start_date = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)
            prev_yr_start_date = datetime.datetime.strptime(prev_yr_start_date, DEFAULT_SERVER_DATE_FORMAT)
            prev_yr_end_date = datetime.datetime.strptime(prev_yr_end_date, DEFAULT_SERVER_DATE_FORMAT)

        previous_year = int(form['year_id'][1]) - 1
        batchdate = datetime.datetime.strptime(form['batch_date'], DEFAULT_SERVER_DATE_FORMAT)
        batchdate = batchdate.strftime('%Y%m%d')
        total_detail_record = 0
        contract_ids = contract_obj.search(self.cr, self.uid, [('employee_id','in',form.get('employee_ids'))]) #, ('date_start','<=', end_date), '|', ('date_end', '>=', end_date),('date_end','=',False)
        vals = []
        emp_ids = employee_obj.search(self.cr, self.uid, [('id', 'in', form.get('employee_ids'))], order='name ASC')
        for employee in employee_obj.browse(self.cr, self.uid, emp_ids):
            res = {}
            contract_ids = contract_obj.search(self.cr, self.uid, [('employee_id', '=', employee.id)])
            contract_income_tax_ids = hr_contract_income_tax_obj.search(self.cr, self.uid, [('contract_id','in',contract_ids),('year_id','=',form['year_id'][0])])
            if contract_income_tax_ids:
                emp = hr_contract_income_tax_obj.browse(self.cr, self.uid, contract_income_tax_ids[0])
                total_detail_record += 1
                sex = birthday = join_date = cessation_date = bonus_declare_date = approve_director_fee_date = fromdate = todate = approval_date = ''
                res['employee'] = employee.name
                if employee.gender == 'male':
                    sex = 'M'
                if employee.gender == 'female':
                    sex = 'F'
                if employee.birthday:
                    birthday = datetime.datetime.strptime(employee.birthday, DEFAULT_SERVER_DATE_FORMAT)
                    birthday = birthday.strftime('%Y-%m-%d')
                if employee.join_date:
                    join_date = datetime.datetime.strptime(employee.join_date, DEFAULT_SERVER_DATE_FORMAT)
                    join_date = join_date.strftime('%Y-%m-%d')
                if employee.cessation_date:
                    cessation_date = datetime.datetime.strptime(employee.cessation_date, DEFAULT_SERVER_DATE_FORMAT)
                    cessation_date = cessation_date.strftime('%Y-%m-%d')
                if emp.bonus_declaration_date:
                    bonus_declare_date = datetime.datetime.strptime(emp.bonus_declaration_date, DEFAULT_SERVER_DATE_FORMAT)
                    bonus_declare_date = bonus_declare_date.strftime('%Y-%m-%d')
                if emp.director_fee_approval_date:
                    approve_director_fee_date = datetime.datetime.strptime(emp.director_fee_approval_date, DEFAULT_SERVER_DATE_FORMAT)
                    approve_director_fee_date = approve_director_fee_date.strftime('%Y-%m-%d')
                if emp.fromdate:
                    fromdate = datetime.datetime.strptime(emp.fromdate, DEFAULT_SERVER_DATE_FORMAT)
                    fromdate = fromdate.strftime('%Y-%m-%d')
                if emp.todate:
                    todate = datetime.datetime.strptime(emp.todate, DEFAULT_SERVER_DATE_FORMAT)
                    todate = todate.strftime('%Y-%m-%d')
                if emp.approval_date:
                    approval_date = datetime.datetime.strptime(emp.approval_date, DEFAULT_SERVER_DATE_FORMAT)
                    approval_date = approval_date.strftime('%Y-%m-%d')
                transport_allowance = salary_amt = other_allowance = other_data = amount_data = mbf_amt = donation_amt = catemp_amt = net_amt = bonus_amt = prv_yr_gross_amt = gross_amt = gross_commission = ybf= 0
                prev_yr_payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', prev_yr_start_date), ('date_from', '<=', prev_yr_end_date), ('employee_id', '=', employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                for payslip in payslip_obj.browse(self.cr, self.uid, prev_yr_payslip_ids):
                    for line in payslip.line_ids:
                        if line.code == 'GROSS':
                            prv_yr_gross_amt += line.amount
                payslip_ids = payslip_obj.search(self.cr, self.uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', employee.id), ('state', 'in', ['draft', 'done', 'verify'])])
                for payslip in payslip_obj.browse(self.cr, self.uid, payslip_ids):
                    fromdate = datetime.datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT)
                    todate = datetime.datetime.strptime(payslip.date_to, DEFAULT_SERVER_DATE_FORMAT)
                    fromdate = fromdate.strftime('%Y')
                    todate = todate.strftime('%Y')
                    basic_flag = False
                    for line in payslip.line_ids:
                        if line.code == 'BASIC':
                            basic_flag = True
                    if basic_flag and emp.contract_id.wage:
                        salary_amt += emp.contract_id.wage
                    for line in payslip.line_ids:
                        if not emp.contract_id.wage and emp.contract_id.rate_per_hour and line.code == 'SC100':
                            salary_amt += line.amount
                        if line.code == 'CPFMBMF':
                            mbf_amt += line.amount
                        if line.code in ['CPFMBMF', 'CPFSINDA', 'CPFCDAC', 'CPFECF']:
                            donation_amt += line.amount
                        if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                            catemp_amt += line.amount
                        if line.code == 'TA':
                            transport_allowance += line.amount
                        if line.code == 'NET':
                            net_amt += line.amount
                        if line.code == 'SC121':
                            bonus_amt += line.amount
                            salary_amt -= line.amount
                        if line.category_id.code == 'BASIC':
#                            salary_amt += line.amount
                            gross_amt += line.amount
                        if line.code in ['SC102', 'SC103']:
                            gross_amt += line.amount
                        if line.category_id.code in ['ADD', 'ALW']:
                            other_data += line.amount
                            salary_amt += line.amount
                        if line.code in ['SC200', 'SC206']:
                            salary_amt -= line.amount
                        if line.code in ['SC104', 'SC105']:
                            salary_amt -= line.amount
                            gross_commission += line.amount
                        if line.category_id.code == 'ALW' and line.code != 'TA':
                            other_allowance += line.amount
#                        
                mbf_amt = mbf_amt
                ybf_amt = emp.ymf
                catemp_amt = catemp_amt
                net_amt = net_amt
                bonus_amt = bonus_amt
                insurance = director_fee = gain_profit = exempt_income = benifits_in_kinds = gains_profit_share_option = excess_voluntary_contribution_cpf_employer = contribution_employer = retirement_benifit_from = retirement_benifit_up = compensation_loss_office = gratuity_payment_amt = entertainment_allowance = pension = 0
                insurance = emp.insurance
                director_fee = emp.director_fee
                gain_profit = emp.gain_profit
                exempt_income = emp.exempt_income
                employment_income = emp.employment_income
                pension = emp.pension or 0.0
                entertainment_allowance = emp.entertainment_allowance
                gratuity_payment_amt = emp.gratuity_payment_amt * 100
                compensation_loss_office = emp.compensation_loss_office
                retirement_benifit_up = emp.retirement_benifit_up
                retirement_benifit_from = emp.retirement_benifit_from
                contribution_employer = emp.contribution_employer
                excess_voluntary_contribution_cpf_employer = emp.excess_voluntary_contribution_cpf_employer
                CPF_designated_pension_provident_fund = emp.CPF_designated_pension_provident_fund
                gains_profit_share_option = emp.gains_profit_share_option
                benifits_in_kinds = emp.benifits_in_kinds
                prv_yr_gross_amt = prv_yr_gross_amt
                other_allowance += emp.other_allowance
#                transport_allowance = entertainment_allowance = 0.00
                total_d_2 = (transport_allowance ) + (entertainment_allowance) + (other_allowance)
                other_data+=total_d_2
#                other_data = (int(gross_commission) or 0) + (int(emp.pension) or 0) + (int(transport_allowance) or 0) + \
#                                (int(entertainment_allowance) or 0) + (int(other_allowance) or 0) + \
#                                (int(emp.retirement_benifit_from) or 0) + (int(emp.contribution_employer) or 0) + \
#                                (int(emp.excess_voluntary_contribution_cpf_employer) or 0) + (int(emp.gains_profit_share_option) or 0) + \
#                                (int(emp.benifits_in_kinds) or 0)
                                
                amount_data = other_data + int(net_amt) + int(emp.director_fee) + int(bonus_amt)
                if not employee.gender:
                    raise osv.except_osv(_('Error'), _('There is no gender define for %s employee.' % (employee.name) ))
                if not employee.birthday:
                    raise osv.except_osv(_('Error'), _('There is no birth date define for %s employee.' % (employee.name) ))
                if not employee.identification_id:
                    raise osv.except_osv(_('Error'), _('There is no identification no define for %s employee.' % (employee.name) ))
                payment_period_form_date = fiscal_start_date
                payment_period_to_date = fiscal_end_date
                if cessation_date:
                    payment_period_to_date = cessation_date
                resource_ids = resource_pool.search(self.cr, self.uid, [('user_id', '=', int(form.get('payroll_user')))])
                emp_id = employee_obj.search(self.cr, self.uid, [('resource_id', 'in', resource_ids)])
                res['autho_user'] = ''
                res['designation'] = ''
                res['tel_no'] = ''
                if emp_id:
                    emp_rec = employee_obj.browse(self.cr, self.uid, emp_id[0])
                    res['autho_user'] = emp_rec.name
                    res['designation'] = emp_rec.job_id and emp_rec.job_id.name or ''
                    res['tel_no'] = emp_rec.mobile_phone or ''
                res['date_today'] = datetime.date.today()
                employee_income_tax = emp.employee_income_tax
                res['employee_income_tax'] = ''
                res['is_income'] = 'YES'
                if employee_income_tax == 'F':
                    res['employee_income_tax'] = 'Tax fully borne by employer on employment income only'
                elif employee_income_tax == 'P':
                    res['employee_income_tax'] = 'Tax partially borne by employer on certain employment income items'
                elif employee_income_tax == 'H':
                    res['employee_income_tax'] = 'A fixed amount of income tax liability borne by employee. Not applicable if income tax is fully paid by employee'
                elif employee_income_tax == 'N':
                    res['employee_income_tax'] = 'Not Applicable'
                else:
                    res['is_income'] = 'NO'
                res['gratu'] = ''
                res['n_pay'] = ''
                res['gratia'] = ''
                res['other'] = ''
                if emp.gratuity_payment == 'Y':
                    res['gratu'] = 'YES'
                    res['n_pay'] = 'YES'
                    res['gratia'] = 'YES'
                    res['other'] = 'YES'
                elif emp.gratuity_payment == 'N':
                    res['gratu'] = 'NO'
                    res['n_pay'] = 'NO'
                    res['gratia'] = 'NO'
                    res['other'] = 'NO'
                #Round down
                res['gross_amt'] = int(gross_amt) * 1.00
                res['fund_name'] = emp.fund_name or ''
                res['identification_id'] = employee.identification_id
                res['employeer_tax'] = employee.company_id.vat
                employee_address = ''
                if employee.address_home_id:
                    employee_address = partner_obj._display_address(self.cr, self.uid, employee.address_home_id, without_company=True)
                res['address_home'] = employee_address or ''
                res['cessation_date'] = cessation_date
                res['sex']= sex
                res['birthday']= birthday
                res['net_amt'] = int(net_amt) * 1.00
                res['bonus_amt'] = int(bonus_amt) * 1.00
                res['director_fee'] = int(director_fee) * 1.00
                res['pension'] = int(pension) * 1.00
                res['transport_allowance'] = int(transport_allowance) * 1.00
                res['entertainment_allowance'] =  int(entertainment_allowance) * 1.00
                res['other_allowance'] = int(other_allowance) * 1.00
                res['total_d_2'] = int(total_d_2) * 1.00
                res['gratuity_payment_amt'] = int(gratuity_payment_amt) * 1.00
                res['nationality'] = employee.empnationality_id.name or ''
                res['amount_data'] = int(amount_data) * 1.00
                res['other_data'] = int(other_data) * 1.00
                res['payment_period_form_date'] = payment_period_form_date
                res['payment_period_to_date'] = payment_period_to_date
                res['mbf_amt'] = int(mbf_amt) * 1.00
                
                if CPF_designated_pension_provident_fund:
                    CPF_designated_pension_provident_fund = CPF_designated_pension_provident_fund%1 >0.00 and (int(CPF_designated_pension_provident_fund) + 1) or CPF_designated_pension_provident_fund
                res['CPF_designated_pension_provident_fund'] = int(CPF_designated_pension_provident_fund) * 1.00
                if donation_amt:
                    donation_amt = donation_amt%1 > 0.00 and (int(donation_amt) + 1) or donation_amt
                res['donation_amt'] = int(donation_amt) * 1.00
                res['donation_amt'] = donation_amt
                
                res['catemp_amt'] = catemp_amt
                if gross_commission:
                    fromdate = '01/01/%s'%str(fromdate)
                    todate = '31/12/%s'%str(todate)
                else:
                    fromdate = ''
                    todate = ''
                res['insurance'] = int(insurance) * 1.00
                res['gain_profit'] = int(gain_profit) * 1.00
                res['exempt_income'] = int(exempt_income) * 1.00
                res['employment_income'] = emp.employee_income_tax == 'H' and int(employment_income) *1.00 or ''
                res['prv_yr_gross_amt'] = int(prv_yr_gross_amt) * 1.00
                res['fromdate'] = fromdate or ''
                res['todate'] = todate or ''
                res['gross_commission'] = int(gross_commission) * 1.00
                res['approval_date'] = approval_date
                res['compensation_loss_office'] = int(compensation_loss_office) * 1.00
                res['prv_yr_gross_amt'] = int(prv_yr_gross_amt) * 1.00
                res['benefits_kind'] =  emp.benefits_kind or ''
                res['section_applicable'] =  emp.section_applicable or ''
                res['gratuity_payment'] =  emp.gratuity_payment or ''
                res['compensation'] =  emp.compensation or ''
                res['cessation_provisions'] =  employee.cessation_provisions or ''
                res['approve_obtain_iras'] =  emp.approve_obtain_iras or ''
                res['from_ir8s'] =  emp.from_ir8s or ''
                res['exempt_remission'] = False
                if emp.exempt_remission != 'N':
                    res['exempt_remission'] =  int(emp.exempt_remission) * 1.00
                res['gross_commission_indicator'] =  int(emp.gross_commission_indicator) * 1.00
                res['retirement_benifit_up'] =  int(retirement_benifit_up) * 1.00
                res['retirement_benifit_from'] =  int(retirement_benifit_from) * 1.00
                res['contribution_employer'] =  int(contribution_employer) * 1.00
                res['excess_voluntary_contribution_cpf_employer'] =  int(excess_voluntary_contribution_cpf_employer) * 1.00
                res['gains_profit_share_option'] =  int(gains_profit_share_option) * 1.00
                res['benifits_in_kinds'] =  int(benifits_in_kinds) * 1.00
                res['job_name'] =  employee.job_id.name or ''
                res['join_date'] =  join_date
                res['bonus_declare_date'] =  bonus_declare_date
                res['approve_director_fee_date'] =  approve_director_fee_date
                res['fund_name'] =  emp.fund_name or ''
                res['deginated_pension'] =  emp.deginated_pension or ''
                res['previous_year'] = previous_year
#                 #Lets be smart!
#                 #Rather than doing change on all amounts, do here
#                 #if any values in IR8A PDF are empty meaning 0.00, it must display the characters NA
#                 #This should have been done smartly for rounding up and down too!
#                 for reskey in res.keys():
#                     if isinstance(res[reskey], float) and not res[reskey]:
#                         res[reskey] = 'NA'
                vals.append(res)
        return vals

report_sxw.report_sxw('report.ppd_ir8a_form_report','hr.payslip','addons/sg_income_tax_report/report/ir8a_form_report_tmpl.rml',parser=ppd_ir8a_form)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: