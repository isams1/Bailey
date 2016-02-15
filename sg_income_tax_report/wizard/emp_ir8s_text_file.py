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
import base64
import tempfile
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from time import gmtime, strftime
from openerp import tools

class emp_ir8s_text_file(osv.osv):

    _name = 'emp.ir8s.text.file'

    def _get_payroll_user_name(self, cr, uid, context=None):
        if context is None:
            context = {}
        supervisors_list = [(False,'')]
        data_obj = self.pool.get('ir.model.data')
        result_data = data_obj._get_id(cr, uid, 'l10n_sg_hr_payroll', 'group_hr_payroll_admin')
        model_data = data_obj.browse(cr, uid, result_data, context=context)
        group_data = self.pool.get('res.groups').browse(cr, uid, model_data.res_id, context)
        for user in group_data.users:
            supervisors_list.append((tools.ustr(user.id), tools.ustr(user.name)))
        return supervisors_list

    _columns = {
            'employee_ids': fields.many2many('hr.employee', 'hr_employe_ir8s_txt_rel', 'emp_id', 'employee_id', 'Employee', required=True),
            'year_id': fields.many2one('account.fiscalyear', 'Accounting Year', required=True),
            'source': fields.selection([('1', 'Mindef'), ('2', 'Government Department'), ('5', 'Statutory Board'),
                                        ('6', 'Private Sector'), ('9', 'Others')], string='Source', required=True),
            'organization_id_type': fields.selection([('7', 'UEN - Business'), ('8', 'UEN - Local'), ('A', 'ASGD'),
                                                      ('I', 'ITR'), ('U', 'UENO')], string='Organization ID Type', required=True),
            'organization_id_no': fields.char('Organization ID No', size=16, required=True),
            'batch_indicatior': fields.selection([('O', 'Original'), ('A', 'Amendment')], string='Batch Indicator', required=True),
            'batch_date': fields.date('Batch Date', required=True),
            'payroll_user': fields.selection(_get_payroll_user_name, 'Name of authorised person', size=128, required=True),
            'print_type' : fields.selection([('text','Text'), ('pdf', 'PDF')], 'Print as', required=True)

    }
    
    _defaults = {
        'print_type' : 'text'
    }    
    
    def download_ir8s_txt_file(self, cr, uid, ids, context):
        context.update({'active_test': False})
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        try:
            fiscal_year = int(data['year_id'][1])
        except:
            raise osv.except_osv(_('Warning'), _('Fiscal Year name must be in digit instead of this "%s".' % (data['year_id'][1])))
        context.update({'employe_id': data['employee_ids'], 'datas': data})
        if data.get('print_type', '') == 'text':
            return {
              'name': _('Binary'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'binary.ir8s.text.file.wizard',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
            }
        elif data.get('print_type', '') == 'pdf':
            data = {
                'ids' : [],
                'model' : 'hr.payslip',
                'form' : data
            }
            ret =  {
                'type' : 'ir.actions.report.xml',
                'report_name' : 'ppd_ir8s_form_report',
                'datas' : data
            }
            return ret

emp_ir8s_text_file()

class binary_ir8s_text_file_wizard(osv.osv_memory):

    _name = 'binary.ir8s.text.file.wizard'

    _columns = {
        'name': fields.char('Name', size=64),
        'ir8s_txt_file': fields.binary('Click On Download Link To Download File', readonly=True),
    }

    def _generate_ir8s_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        hr_contract_income_tax_obj = self.pool.get('hr.contract.income.tax')
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        start_date = end_date = False
        if context.get('datas')['year_id'][1]:
            start_date = '%s-01-01' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            end_date = '%s-12-31' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            start_date = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            batchdate = datetime.datetime.strptime(context.get('datas')['batch_date'], DEFAULT_SERVER_DATE_FORMAT)
            batchdate = batchdate.strftime('%Y%m%d')
            server_date = strftime("%Y%m%d", gmtime())
            emp_id = employee_obj.search(cr, uid, [('user_id', '=', int(context.get('datas')['payroll_user']))])
            emp_designation = ''
            user_obj = self.pool.get('res.users')
            payroll_admin_user_name = user_obj.browse(cr, uid, int(context.get('datas')['payroll_user'])).name
            company_name = user_obj.browse(cr, uid, int(context.get('datas')['payroll_user'])).company_id.name
            for emp in employee_obj.browse(cr, uid, emp_id):
                emp_designation = emp.job_id.name
                emp_email = emp.work_email
                emp_contact = emp.work_phone
            header_record = '0'.ljust(1) + \
                            tools.ustr(context.get('datas')['source'] or '').ljust(1) + \
                            tools.ustr(context.get('datas')['year_id'][1] or '').ljust(4) + \
                            tools.ustr(context.get('datas')['organization_id_type'] or '').ljust(1) + \
                            tools.ustr(context.get('datas')['organization_id_no'] or '').ljust(12) + \
                            tools.ustr(payroll_admin_user_name or '')[:30].ljust(30) + \
                            tools.ustr(emp_designation)[:30].ljust(30) + \
                            tools.ustr(company_name)[:60].ljust(60) + \
                            tools.ustr(emp_contact)[:20].ljust(20) + \
                            tools.ustr(emp_email)[:60].ljust(60) + \
                            tools.ustr(context.get('datas')['batch_indicatior'] or '').ljust(1) + \
                            tools.ustr(server_date).ljust(8) + \
                            ''.ljust(30) + \
                            ''.ljust(10) + \
                            ''.ljust(932) + "\r\n"
            tmp_file.write(header_record)
            
            contract_ids = contract_obj.search(cr, uid, [('employee_id','in',context.get('employe_id'))])
            for contract in contract_obj.browse(cr, uid, contract_ids):
                contract_income_tax_ids = hr_contract_income_tax_obj.search(cr, uid, [('contract_id','=',contract.id),('year_id','=',context.get('datas')['year_id'][0])])
                if contract_income_tax_ids:
                    for emp in hr_contract_income_tax_obj.browse(cr, uid, [contract_income_tax_ids[0]]):
                        payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', contract.employee_id.id), ('state', 'in', ['draft', 'done', 'verify'])])
                        jan_gross_amt = feb_gross_amt = march_gross_amt = apr_gross_amt = may_gross_amt = june_gross_amt = july_gross_amt = aug_gross_amt = sept_gross_amt = oct_gross_amt = nov_gross_amt = dec_gross_amt = 0
                        jan_empoyer_amt = feb_empoyer_amt = march_empoyer_amt = apr_empoyer_amt = may_empoyer_amt = june_empoyer_amt = july_empoyer_amt = aug_empoyer_amt = sept_empoyer_amt = oct_empoyer_amt = nov_empoyer_amt = dec_empoyer_amt = 0
                        jan_empoyee_amt = feb_empoyee_amt = march_empoyee_amt = apr_empoyee_amt = may_empoyee_amt = june_empoyee_amt = july_empoyee_amt = aug_empoyee_amt = sept_empoyee_amt = oct_empoyee_amt = nov_empoyee_amt = dec_empoyee_amt = 0
                        tot_gross_amt = tot_empoyee_amt = tot_empoyer_amt = 0
                        
                        additional_wage_from_date = additional_wage_to_date = fromdate = todate = add_wage_date = eyer_date = eyee_date = ''
                        if emp.year_id.date_start:
                            fromdate = datetime.datetime.strptime(emp.year_id.date_start, DEFAULT_SERVER_DATE_FORMAT)
                            fromdate = fromdate.strftime('%Y%m%d')
                        if emp.year_id.date_stop:
                            todate = datetime.datetime.strptime(emp.year_id.date_stop, DEFAULT_SERVER_DATE_FORMAT)
                            todate = todate.strftime('%Y%m%d')
                        if emp.add_wage_pay_date:
                            add_wage_date = datetime.datetime.strptime(emp.add_wage_pay_date, DEFAULT_SERVER_DATE_FORMAT)
                            add_wage_date = add_wage_date.strftime('%Y%m%d')
                        if emp.refund_eyers_date:
                            eyer_date = datetime.datetime.strptime(emp.refund_eyers_date, DEFAULT_SERVER_DATE_FORMAT)
                            eyer_date = eyer_date.strftime('%Y%m%d')
                        if emp.refund_eyees_date:
                            eyee_date = datetime.datetime.strptime(emp.refund_eyees_date, DEFAULT_SERVER_DATE_FORMAT)
                            eyee_date = eyee_date.strftime('%Y%m%d')
                        
                        eyer_contibution=eyee_contibution=additional_wage=refund_eyers_contribution=refund_eyers_interest_contribution=refund_eyees_contribution=refund_eyees_interest_contribution=0
                        eyer_contibution = '%0*d' % (7, int(abs(emp.eyer_contibution)))
                        eyee_contibution = '%0*d' % (7, int(abs(emp.eyee_contibution)))
                        additional_wage = '%0*d' % (7, int(abs(emp.additional_wage)))
                        refund_eyers_contribution= '%0*d' % (7, int(abs(emp.refund_eyers_contribution)))
                        refund_eyers_interest_contribution= '%0*d' % (7, int(abs(emp.refund_eyers_interest_contribution)))
                        refund_eyees_contribution='%0*d' % (7, int(abs(emp.refund_eyees_contribution)))
                        refund_eyees_interest_contribution = '%0*d' % (7, int(abs(emp.refund_eyees_interest_contribution)))
                        if emp.additional_wage:
                            additional_wage_from_date = fromdate
                            additional_wage_to_date = todate
                        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                            payslip_month = ''
                            payslip_month = datetime.datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT)
                            payslip_month = payslip_month.strftime('%m')
                            gross_amt = empoyer_amt = empoyee_amt = 0
                            for line in payslip.line_ids:
                                if line.code == 'GROSS':
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
                        
                        jan_gross_amt = '%0*d' % (9, int(abs(jan_gross_amt * 100)))
                        jan_empoyer_amt = '%0*d' % (9, int(abs(jan_empoyer_amt * 100)))
                        jan_empoyee_amt = '%0*d' % (9, int(abs(jan_empoyee_amt * 100)))
                        
                        feb_gross_amt = '%0*d' % (9, int(abs(feb_gross_amt * 100)))
                        feb_empoyer_amt = '%0*d' % (9, int(abs(feb_empoyer_amt * 100)))
                        feb_empoyee_amt = '%0*d' % (9, int(abs(feb_empoyee_amt * 100)))
                        
                        march_gross_amt = '%0*d' % (9, int(abs(march_gross_amt * 100)))
                        march_empoyer_amt = '%0*d' % (9, int(abs(march_empoyer_amt * 100)))
                        march_empoyee_amt = '%0*d' % (9, int(abs(march_empoyee_amt * 100)))
                        
                        apr_gross_amt = '%0*d' % (9, int(abs(apr_gross_amt * 100)))
                        apr_empoyer_amt = '%0*d' % (9, int(abs(apr_empoyer_amt * 100)))
                        apr_empoyee_amt = '%0*d' % (9, int(abs(apr_empoyee_amt * 100)))
                        
                        may_gross_amt = '%0*d' % (9, int(abs(may_gross_amt * 100)))
                        may_empoyer_amt = '%0*d' % (9, int(abs(may_empoyer_amt * 100)))
                        may_empoyee_amt = '%0*d' % (9, int(abs(may_empoyee_amt * 100)))
                        
                        june_gross_amt = '%0*d' % (9, int(abs(june_gross_amt * 100)))
                        june_empoyer_amt = '%0*d' % (9, int(abs(june_empoyer_amt * 100)))
                        june_empoyee_amt = '%0*d' % (9, int(abs(june_empoyee_amt * 100)))
                        
                        july_gross_amt = '%0*d' % (9, int(abs(july_gross_amt * 100)))
                        july_empoyer_amt = '%0*d' % (9, int(abs(july_empoyer_amt * 100)))
                        july_empoyee_amt = '%0*d' % (9, int(abs(july_empoyee_amt * 100)))
                        
                        aug_gross_amt = '%0*d' % (9, int(abs(aug_gross_amt * 100)))
                        aug_empoyer_amt = '%0*d' % (9, int(abs(aug_empoyer_amt * 100)))
                        aug_empoyee_amt = '%0*d' % (9, int(abs(aug_empoyee_amt * 100)))
                        
                        sept_gross_amt = '%0*d' % (9, int(abs(sept_gross_amt * 100)))
                        sept_empoyer_amt = '%0*d' % (9, int(abs(sept_empoyer_amt * 100)))
                        sept_empoyee_amt = '%0*d' % (9, int(abs(sept_empoyee_amt * 100)))
                        
                        oct_gross_amt = '%0*d' % (9, int(abs(oct_gross_amt * 100)))
                        oct_empoyer_amt = '%0*d' % (9, int(abs(oct_empoyer_amt * 100)))
                        oct_empoyee_amt = '%0*d' % (9, int(abs(oct_empoyee_amt * 100)))
                        
                        nov_gross_amt = '%0*d' % (9, int(abs(nov_gross_amt * 100)))
                        nov_empoyer_amt = '%0*d' % (9, int(abs(nov_empoyer_amt * 100)))
                        nov_empoyee_amt = '%0*d' % (9, int(abs(nov_empoyee_amt * 100)))
                        
                        dec_gross_amt = '%0*d' % (9, int(abs(dec_gross_amt * 100)))
                        dec_empoyer_amt = '%0*d' % (9, int(abs(dec_empoyer_amt * 100)))
                        dec_empoyee_amt = '%0*d' % (9, int(abs(dec_empoyee_amt * 100)))
                        
                        tot_gross_amt = '%0*d' % (7, int(abs(tot_gross_amt)))
                        tot_empoyer_amt = '%0*d' % (7, int(abs(tot_empoyer_amt)))
                        tot_empoyee_amt = '%0*d' % (7, int(abs(tot_empoyee_amt)))

                        if not contract.employee_id.identification_no:
                            raise osv.except_osv(_('Error'), _('There is no ID Type of Employee define for %s employee.' % (contract.employee_id.name) ))
                        if not contract.employee_id.identification_id:
                            raise osv.except_osv(_('Error'), _('There is no identification no define for %s employee.' % (contract.employee_id.name) ))
                        if not contract.employee_id.work_phone or not contract.employee_id.work_email:
                            raise osv.except_osv(_('Error'), _('You must be configure Contact no or email for %s employee.' % (contract.employee_id.name) ))

                        detail_record = '1'.ljust(1) + \
                                        tools.ustr(contract.employee_id.identification_no or '').ljust(1) + \
                                        tools.ustr(contract.employee_id.identification_id or '')[:12].ljust(12) + \
                                        tools.ustr(contract.employee_id.name or '')[:80].ljust(80) + \
                                        tools.ustr(jan_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(jan_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(jan_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(feb_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(feb_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(feb_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(march_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(march_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(march_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(apr_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(apr_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(apr_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(may_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(may_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(may_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(june_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(june_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(june_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(july_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(july_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(july_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(aug_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(aug_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(aug_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(sept_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(sept_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(sept_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(oct_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(oct_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(oct_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(nov_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(nov_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(nov_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(dec_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(dec_empoyer_amt)[:9].ljust(9) + \
                                        tools.ustr(dec_empoyee_amt)[:9].ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        ''.ljust(9) + \
                                        tools.ustr(tot_gross_amt)[:7].ljust(7) + \
                                        tools.ustr(tot_empoyer_amt)[:7].ljust(7) + \
                                        tools.ustr(tot_empoyee_amt)[:7].ljust(7) + \
                                        ''.ljust(7) + \
                                        ''.ljust(7) + \
                                        ''.ljust(7) + \
                                        tools.ustr(fromdate).ljust(8) + \
                                        tools.ustr(todate).ljust(8) + \
                                        tools.ustr(emp.indicator_for_CPF_contributions or '').ljust(1) + \
                                        tools.ustr(emp.CPF_capping_indicator or '').ljust(1) + \
                                        tools.ustr(emp.singapore_permanent_resident_status or '').ljust(1) + \
                                        tools.ustr(emp.approval_has_been_obtained_CPF_board or '').ljust(1) + \
                                        tools.ustr(eyer_contibution)[:7].ljust(7) + \
                                        tools.ustr(eyee_contibution)[:7].ljust(7) + \
                                        tools.ustr(additional_wage)[:7].ljust(7) + \
                                        tools.ustr(additional_wage_from_date).ljust(8) + \
                                        tools.ustr(additional_wage_to_date).ljust(8) + \
                                        tools.ustr(add_wage_date).ljust(8) + \
                                        tools.ustr(refund_eyers_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyers_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyer_date).ljust(8) + \
                                        tools.ustr(refund_eyees_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyees_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyee_date).ljust(8) + \
                                        tools.ustr(additional_wage)[:7].ljust(7) + \
                                        tools.ustr(additional_wage_from_date).ljust(8) + \
                                        tools.ustr(additional_wage_to_date).ljust(8) + \
                                        tools.ustr(add_wage_date).ljust(8) + \
                                        tools.ustr(refund_eyers_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyers_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyer_date).ljust(8) + \
                                        tools.ustr(refund_eyees_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyees_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyee_date).ljust(8) + \
                                        tools.ustr(additional_wage)[:7].ljust(7) + \
                                        tools.ustr(additional_wage_from_date).ljust(8) + \
                                        tools.ustr(additional_wage_to_date).ljust(8) + \
                                        tools.ustr(add_wage_date).ljust(8) + \
                                        tools.ustr(refund_eyers_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyers_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyer_date).ljust(8) + \
                                        tools.ustr(refund_eyees_contribution)[:7].ljust(7) + \
                                        tools.ustr(refund_eyees_interest_contribution)[:7].ljust(7) + \
                                        tools.ustr(eyee_date).ljust(8) + \
                                        ''.ljust(107) + \
                                        ''.ljust(50) + \
                                         "\r\n"
                        tmp_file.write(detail_record)
        
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        
        return base64.b64encode(out)

    _defaults = {
         'name': 'IR8S.txt',
         'ir8s_txt_file': _generate_ir8s_file,
    }

binary_ir8s_text_file_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: