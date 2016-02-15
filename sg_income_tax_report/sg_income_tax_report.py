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
from openerp.osv import osv, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_contract(osv.Model):
    _inherit = 'hr.contract'

    _columns = {
        'hr_contract_income_tax_ids': fields.one2many('hr.contract.income.tax', 'contract_id', 'Income Tax'),
    }

class hr_contract_income_tax(osv.Model):

    _name = 'hr.contract.income.tax'
    _rec_name = 'contract_id'

    def _get_payroll_computational_data(self, cr, uid, ids, name, args, context=None):
        res={}
        payslip_obj = self.pool.get('hr.payslip')
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = {
                    'mbf': 0.0,
                    'donation': 0.0,
                    'CPF_designated_pension_provident_fund':0.0,
                    'payslip_net_amount': 0.0,
                    'bonus_amount': 0.0
            }
            mbf = donation = CPF_designated_pension_provident_fund = payslip_net_amount = bonus_amount = 0.00
            start_date = datetime.strptime(data.year_id.date_start, DEFAULT_SERVER_DATE_FORMAT)
            fiscal_year = start_date.year
            start_date = datetime.strptime(str(start_date.day) + "-" + str(start_date.month) + "-" + str(fiscal_year -1), '%d-%m-%Y')
            start_date = start_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(data.year_id.date_stop, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(str(end_date.day) + "-" + str(end_date.month) + "-" + str(fiscal_year -1), '%d-%m-%Y')
            end_date = end_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', data.contract_id.employee_id.id), ('state', 'in', ['draft', 'done', 'verify'])])
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                for line in payslip.line_ids:
                    if line.code == 'CPFMBMF':
                        mbf += line.amount
                    if line.code in ['CPFMBMF', 'CPFSINDA', 'CPFCDAC', 'CPFECF']:
                        donation += line.amount
                    if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                        CPF_designated_pension_provident_fund += line.amount
                    if line.code == 'GROSS':
                        payslip_net_amount += line.amount
                    if line.amount == 'SC121':
                        bonus_amount += line.amount
            res[data.id]['mbf'] = mbf or 0.0
            res[data.id]['mbf'] = data.mbf_handler or mbf or 0.0
            res[data.id]['donation'] = donation or 0.0
            res[data.id]['CPF_designated_pension_provident_fund'] = CPF_designated_pension_provident_fund or 0.0
            res[data.id]['payslip_net_amount'] = payslip_net_amount or 0.0
            res[data.id]['bonus_amount'] = bonus_amount or 0.0
        return res

    def _mbf_search(self, cr, uid, id, name, value, arg, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, id, {'mbf_handler': value}, context=context)
        return True
    
    def _cpf_search(self, cr, uid, id, name, value, arg, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, id, {'CPF_designated_pension_provident_fund_handler': value}, context=context)
        return True
    
    def _donation_search(self, cr, uid, id, name, value, arg, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, id, {'donation_handler': value}, context=context)
        return True
    
    _columns = {
            'contract_id': fields.many2one('hr.contract', 'Contract'),
            'year_id': fields.many2one('account.fiscalyear', 'Year Of Assessment'),
            'cessation_date': fields.date('Cessation Date'),
            'director_fee': fields.float('18. Directors fee'),
            'gain_profit': fields.float('19(a). Gains & Profit from Share Options For S10 (1) (g)'),
            'exempt_income': fields.float('20. Exempt Income/ Income subject to Tax Remission'),
            'employment_income': fields.float('21. Amount of employment income for which tax is borne by employer'),
            'benefits_kind': fields.selection([('Y', "Benefits-in-kind rec'd"), ('N', "Benefits-in-kind not rec'd")], string='23. Benefits-in-kind'),
            'section_applicable': fields.selection([('Y', 'S45 applicable'), ('N', 'S45 not applicable')], string='24. Section 45 applicable'),
            'employee_income_tax': fields.selection([('F', 'Tax fully borne by employer on employment income only'), ('P', 'Tax partially borne by employer on certain employment income items'),
                                                     ('H', 'A fixed amount of income tax liability borne by employee. Not applicable if income tax is fully paid by employee'),
                                                     ('N', 'Not Applicable')], string='25. Employees Income Tax borne by employer'),
            'gratuity_payment': fields.selection([('Y', 'Gratuity/ payment in lieu of notice/ex-gratia paid'),
                                                  ('N', 'No Gratuity/ payment in lieu of notice/ex-gratia paid')], string='26. Gratuity/ Notice Pay/ Ex-gratia payment/ Others'),
            'compensation': fields.selection([('Y', ' Compensation / Retrenchment benefits paid'),
                                              ('N', 'No Compensation / Retrenchment benefits paid')], string='27. Compensation for loss of office'),
            'approve_obtain_iras': fields.selection([('Y', 'Approval obtained from IRAS'),
                                                     ('N', 'No approval obtained from IRAS ')], string='27(a). Approval obtained from IRAS'),
            'approval_date': fields.date('27(b). Date of approval'),
            'from_ir8s': fields.selection([('Y', 'IR8S is applicable'), ('N', 'IR8S is not applicable')], string='29. Form IR8S'),
            'exempt_remission': fields.selection([('1', 'Tax Remission on Overseas Cost of Living Allowance (OCLA)'),
                                                  ('2', ' Tax remission on Operation Headquarters (OHQ)'),
                                                  ('3', 'Seaman'), ('4', 'Exemption'),
                                                  ('N', 'Not Applicable')], string='30. Exempt/ Remission income Indicator'),
            'gross_commission': fields.float('31. Gross Commission'),
            'fromdate': fields.date('32(a). From Date'),
            'todate': fields.date('32(b). To Date'),
            'gross_commission_indicator': fields.selection([('M', ' Monthly'), ('O', 'Other than monthly'),
                                                            ('B', 'Both')], string='33. Gross Commission Indicator'),
            'pension': fields.float('34. Pension'),
            'entertainment_allowance': fields.float('36. Entertainment Allowance'),
            'other_allowance': fields.float('37. Other Allowance'),
            'gratuity_payment_amt': fields.float('38. Gratuity/ Notice Pay/ Ex-gratia payment/ Others'),
            'compensation_loss_office': fields.float('38(a). Compensation for loss of office'),
            'retirement_benifit_up': fields.float('39. Retirement benefits accrued up to 31.12.92'),
            'retirement_benifit_from': fields.float('40. Retirement benefits accrued from 1993'),
            'contribution_employer': fields.float('41. Contributions made by employer to any pension / provident fund constituted outside Singapore'),
            'excess_voluntary_contribution_cpf_employer': fields.float('42. Excess / voluntary contribution to CPF by employer'),
            'gains_profit_share_option': fields.float('43. Gains and profits from share options for S10 (1) (b)'),
            'benifits_in_kinds': fields.float('44. Value of benefits-in- kinds'),
            'emp_voluntary_contribution_cpf': fields.float("45. E'yees voluntary contribution to CPF obligatory by contract of employment (overseas posting)"),
            'bonus_declaration_date': fields.date('49. Date of declaration of bonus'),
            'director_fee_approval_date': fields.date('50. Date of approval of directors fees'),
            'fund_name': fields.char('51. Name of fund for Retirement benefits', size=32),
            'deginated_pension': fields.char("52. Name of Designated Pension or Provident Fund for which e'yee made compulsory contribution", size=32),
            'mbf': fields.function(_get_payroll_computational_data, string='12. MBF', fnct_inv= _mbf_search, type='float', multi="payroll_data_all"),
            'mbf_handler' : fields.float('MBF Handler'),
            'donation_handler' : fields.float('Donation Handler'),
            'donation': fields.function(_get_payroll_computational_data, string='13. Donation',fnct_inv= _donation_search, type='float', multi="payroll_data_all"),
            'CPF_designated_pension_provident_fund': fields.function(_get_payroll_computational_data, string='14. CPF/Designated Pension or Provident Fund', fnct_inv= _cpf_search, type='float', multi="payroll_data_all"),
            'CPF_designated_pension_provident_fund_handler' : fields.float('MBF Handler'),
            'indicator_for_CPF_contributions': fields.selection([('Y','Obligatory'), ('N','Not obligatory')], string='84. Indicator for CPF contributions in respect of overseas posting which is obligatory by contract of employment'),
            'CPF_capping_indicator': fields.selection([('Y','Capping has been applied'), ('N','Capping has been not applied')], string='85. CPF capping indicator'),
            'singapore_permanent_resident_status': fields.selection([('Y','Singapore Permanent Resident Status is approved'), 
                                                                     ('N','Singapore Permanent Resident Status is not approved')], string='86. Singapore Permanent Resident Status is approved'),
            'approval_has_been_obtained_CPF_board': fields.selection([('Y',' Approval has been obtained from CPF Board to make full contribution'),
                                                                      ('N',' Approval has NOT been obtained from CPF Board to make full contribution')], string='87. Approval has been obtained from CPF Board to make full contribution'),
            'eyer_contibution': fields.float('88. Eyers Contribution'),
            'eyee_contibution': fields.float('89. Eyees Contribution'),
            'additional_wage': fields.float('99. Additional wages'),
            'add_wage_pay_date': fields.date('101. Date of payment for additional wages'),
            'refund_eyers_contribution': fields.float('102. Amount of refund applicable to Eyers contribution'),
            'refund_eyees_contribution': fields.float('105. Amount of refund applicable to Eyees contribution'),
            'refund_eyers_date': fields.date('104. Date of refund given to employer'),
            'refund_eyees_date': fields.date('107. Date of refund given to employee'),
            'refund_eyers_interest_contribution': fields.float('103. Amount of refund applicable to Eyers Interest on contribution'),
            'refund_eyees_interest_contribution': fields.float('106. Amount of refund applicable to Eyees Interest on contribution'),
            'insurance': fields.float('Insurance'),
            'payslip_net_amount': fields.function(_get_payroll_computational_data, string='Gross Salary, Fees, Leave Pay, Wages and Overtime Pay', type='float', multi="payroll_data_all"),
            'bonus_amount': fields.function(_get_payroll_computational_data, string='Bonus', type='float', multi="payroll_data_all"),
            'ymf' : fields.float('Yayasan Mendaki Fund'),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: