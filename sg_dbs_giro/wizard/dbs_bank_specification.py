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
import time
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class binary_dbs_bank_file_wizard(osv.osv_memory):

    _name = 'binary.dbs.bank.file.wizard'

    _columns = {
        'name': fields.char('Name', size=64),
        'cpf_txt_file': fields.binary('Click On Download Link To Download Text File', readonly=True),
    }

    def _generate_file(self, cr, uid, context = None):
        tgz_tmp_filename = tempfile.mktemp('.'+"txt")
        tmp_file = open(tgz_tmp_filename, "wr")
        try:
            period_obj = self.pool.get("account.period")
            payslip_obj = self.pool.get("hr.payslip")
            if not context.get("month"):
                return False
            period_rec = period_obj.browse(cr, uid, context.get("month"), context = context)
            
            header2_record = ''
            value_date = datetime.datetime.strptime(context.get("value_date"), "%Y-%m-%d")
            """ First 6 digit for date and 45 space in header(Value Date & Filler)"""
            header2_record += value_date.strftime('%y%m%d').ljust(6) + ''.ljust(45) 
            """ Originating Bank Number Value = 7171 """
            header2_record += ('%04d' % context.get('bank_number')).ljust(4)
            """ Originating Branch Number """
#            header2_record += ('%03d' % context.get('batch_number')).ljust(3)
            header2_record += ('%03d' % context.get('branch_number')).ljust(3)
            """ Originating Account Number and 2 space"""
            originator_acc = context.get('account_number').ljust(11)
            header2_record += originator_acc + ''.ljust(2)
            """Originator’s Name"""
            header2_record += (context.get('originator_name')).ljust(20)
            """Message Sequence Number"""
            header2_record += (context.get('msg_seq_no')).ljust(5)
            """Sender’s Company Id & space  & Record Type"""
            header2_record += (context.get('company_name').upper()).ljust(8) + ''.ljust(9) + '0'.ljust(1)
            """Carriage Return <CR> & Line Feed <LF>"""
            header2_record += '\r\n'
            tmp_file.write(header2_record)
            
            employe_obj = self.pool.get("hr.employee")
            emp_ids = employe_obj.search(cr, uid, [('bank_account_id', '!=', False)], order="name", context = context)
            payment_detail = ''
            total_credit_trans = 0
            summary_amount = 0
            hash_total = 0
            total_amount = 0
            for employee in employe_obj.browse(cr, uid, emp_ids, context = context):
                if not employee.bank_account_id:
                    continue
                payslip_id = payslip_obj.search(cr, uid, [('employee_id', '=', employee.id), ('cheque_number','=',False), ('date_from', '>=', period_rec.date_start), ('date_to', '<=', period_rec.date_stop), ('state', 'in', ['done'])])
                if not payslip_id:
                    continue
                """Receiving Bank Number"""
                bank_code = employee.bank_account_id and employee.bank_account_id.bank_bic or ''
                if bank_code.__len__() <= 4:
                    payment_detail += bank_code.rjust(4, '0')
                else:
                    payment_detail += bank_code[0:4].ljust(4)
                """Receiving Branch Number"""
                emp_branch_code = employee.bank_account_id and employee.bank_account_id.branch_id or ''
                if emp_branch_code.__len__() <= 3:
                    payment_detail += emp_branch_code.rjust(3, '0')
                else:
                    payment_detail += emp_branch_code[0:3].ljust(3)
                """Receiving Account Number"""
                emp_bank_ac_no = employee.bank_account_id and employee.bank_account_id.acc_number or ''
                if emp_bank_ac_no.__len__() <= 11:
                    payment_detail += emp_bank_ac_no.ljust(11, ' ')
                else:
                    payment_detail += emp_bank_ac_no[0:11].ljust(11)
                
                receiving_acc_no = ''
                originator_acc_no = ''   
                if emp_bank_ac_no.__len__() <= 11:
                    receiving_acc_no = emp_bank_ac_no.ljust(11, '0')
                else:
                    receiving_acc_no = emp_bank_ac_no[0:11].ljust(11)
                    
                if len(context.get('account_number')) <= 11:
                    originator_acc_no = str(context.get('account_number')).ljust(11, '0')
                else:
                    originator_acc_no = context.get('account_number')[0:11].ljust(11)
                    
                """Derivation of Account Number Hash Total """
                """@note:1)Split the two account numbers into 6 digits and 5 digits 
                     2)Subtract the 5-digit component from the 6-digit component for both 
                     receiving and originating account numbers. 3) Abs value """
                receiving_acc_result = int(receiving_acc_no[:6]) -int(receiving_acc_no[-5:]),
                originator_acc_result = int(originator_acc_no[:6]) - int(originator_acc_no[-5:])
                hash_total += abs((receiving_acc_result and receiving_acc_result[0]) - (originator_acc_result))
                """ Receiving Account Name """
                emp_bank_name = employee.bank_account_id and employee.bank_account_id.owner_name or ''
                if emp_bank_name:
                    if emp_bank_name.__len__() <= 20:
                        payment_detail += emp_bank_name.ljust(20)
                    else:
                        payment_detail += emp_bank_name[0:20].ljust(20)
                else:
                    if employee.name.__len__() <= 20:
                        payment_detail += employee.name.ljust(20)
                    else:
                        payment_detail += employee.name[0:20].ljust(20)
                        
                """Transaction Code"""      
                payment_detail += "22"
                """Amount In Cents"""
                total_amount = 0
                for line in payslip_obj.browse(cr, uid, payslip_id[0]).line_ids:
                    if line.code == "NET":
                        total_amount = line.amount
                if total_amount:
                    total_amount = int(round(total_amount * 100))
                    payment_detail += ('%011d' % total_amount).ljust(11)
                else:
                    payment_detail += ('%011d' % 0).ljust(11)
                summary_amount += total_amount
                """Filler 38 space & Particulars 12 space & Reference 12 & Record Type 1"""    
                payment_detail += "".ljust(62) + '1'
                payment_detail += '\r\n'
                total_credit_trans += 1
            tmp_file.write(payment_detail)
            """ Batch summary"""
            summary_details = ""
            """ Total Number Of Credit Transactions """ 
            summary_details += ('%08d' % total_credit_trans).rjust(8)
            """ Total Credit Amount In Cents """
            summary_details += ('%011d' % summary_amount).rjust(11) 
            """ Filler(5) & Total Number Of Debit Transactions & Total Debit Amount In Cents & Filler(26)"""
            summary_details += ''.ljust(5) + ''.rjust(8, '0') + ''.rjust(11, '0') + ''.ljust(26)
            """ Account Number Hash Total """ 
            summary_details += ('%011d' % hash_total).rjust(11)
            """Filler & Record Type """
            summary_details +=''.ljust(33) + '9'
            summary_details += '\r\n'
            tmp_file.write(summary_details)
        finally:
            tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out) 

    def _get_file_name(self, cr, uid, context=None):
        period_obj = self.pool.get('account.period')
        if context is None:
            context = {}
        period_id = context.get('month')
        if not period_id:
            return 'dbs_txt_file.txt'
        period_data = period_obj.browse(cr, uid, period_id, context=context)
        end_date = datetime.datetime.strptime(period_data.date_stop, DEFAULT_SERVER_DATE_FORMAT)
        monthyear = end_date.strftime('%b%Y')
        file_name = 'dbs_txt_file_' + monthyear + '.txt'
        return file_name

    _defaults = {
                 'name': _get_file_name,
                 'cpf_txt_file': _generate_file,
    }

class dbs_bank_specification(osv.osv_memory):

    _name = 'dbs.bank.specification'

    _columns = {
                'branch_number': fields.integer('Branch Number', size=3, required=True),
                'bank_number': fields.integer('Bank Number', size=4, required=True),
                'batch_number': fields.integer('Batch Number', size=3, required=True),
                'account_number': fields.char('Account Number', size=11, required=True),
                'originator_name': fields.char("Originator's Name", size=20, required=True),
                'originator_name': fields.char("Originator's Name", size=20, required=True),
                'month': fields.many2one('account.period', 'Month', required=True),
                'value_date':fields.date("Value Date", required=True),
                'msg_seq_no':fields.char("Message Sequence Number",size=5, required=True),
                'company_name':fields.char("Company Name",size=8, required=True),
    }

    _defaults = {
         "value_date": lambda *a:datetime.datetime.now().strftime('%Y-%m-%d'),
         "bank_number":'7171',
    }

    def get_text_file(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        bank_data = {}
        data = self.read(cr, uid, ids, [])
        if data:
            bank_data = data[0]
        if bank_data and bank_data.get('branch_number') and len(str(bank_data.get('branch_number'))) > 3:
            raise osv.except_osv(_('Error'), _('Branch number length must be less than or equal to three digits.'))
        if bank_data and bank_data.get('batch_number') and len(str(bank_data.get('batch_number'))) > 3:
            raise osv.except_osv(_('Error'), _('Batch number length must be less than or equal to three digits.'))
        if bank_data and bank_data.get('account_number') and len(str(bank_data.get('account_number'))) > 11:
            raise osv.except_osv(_('Error'), _('Account number length must be less than or equal to eleven digits.'))
        
        context.update({'branch_number': bank_data.get('branch_number'), 'account_number': bank_data.get("account_number"),
                        'month': bank_data.get("month")[0],'value_date': bank_data.get("value_date"), 'batch_number': bank_data.get("batch_number"),
                        'originator_name':bank_data.get('originator_name'),'bank_number':bank_data.get('bank_number'),
                        'msg_seq_no':bank_data.get('msg_seq_no'),'company_name':bank_data.get('company_name')})
        return {
              'name': _('Text file'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'binary.dbs.bank.file.wizard',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: