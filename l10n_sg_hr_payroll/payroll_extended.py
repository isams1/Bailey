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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil import parser, rrule
import math
import openerp.tools.safe_eval
import calendar
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp import api, tools
import time

#openerp.tools.safe_eval._ALLOWED_MODULES.append('math')

class res_partner_bank(osv.Model):
    _inherit = 'res.partner.bank'

    _columns = {
        'branch_id':fields.char("Branch ID", size=48),
    }

class payroll_extended(osv.Model):
    _inherit = 'hr.payslip.input'

    _columns = {
        'code': fields.char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules"),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input"),
    }

class hr_payslip_worked_days(osv.Model):
    _inherit = 'hr.payslip.worked_days'

    _columns = {
        'code': fields.char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules"),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input"),
    }

class hr_payslip_line(osv.Model):
    _inherit = 'hr.payslip.line'

    _columns = {
        'contract_id':fields.many2one('hr.contract', 'Contract', required=False, select=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', required=False),
    }

class hr_salary_rule(osv.Model):
    _inherit = 'hr.salary.rule'
    _columns = {
        'code':fields.char('Code', size=64, required=False, help="The code of salary rules can be used as reference in computation of other rules. In that case, it is case sensitive."),
        'id': fields.integer('ID', readonly=True),
    }

    def compute_rule(self, cr, uid, rule_id, localdict, context=None):
        if localdict is None or not localdict:
            localdict = {}
        localdict.update({'math': math})
        return super(hr_salary_rule, self).compute_rule(cr, uid, rule_id, localdict, context=context)

class hr_payslip(osv.Model):
    _inherit = 'hr.payslip'
    _order = 'employee_name'

    def get_first_day(self, cr, uid, ids, current_date, current_date_years=0, current_date_months=0, context=None):
        # d_years, d_months are "deltas" to apply to dt
        y, m = current_date.year + current_date_years, current_date.month + current_date_months
        a, m = divmod(m-1, 12)
        return date(y+a, m+1, 1)

    def get_last_day(self, cr, uid, ids, current_date, context=None):
        return self.get_first_day(cr, uid, ids, current_date, 0, 1, context=context) + timedelta(-1)

    def _get_hr_analytic_timesheet_ids(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from hr payslip. 
        """
        payslip_obj = self.pool.get('hr.payslip')
        payslip_search_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.user_id:
                payslip_search_ids = payslip_obj.search(cr, uid, [('employee_id.user_id.id', '=', line.user_id.id), 
                                               ('date_from', '<=', line.date),
                                               ('date_to', '>=', line.date),
                                               ('state', 'in', ['draft', 'done', 'verify'])])
        return payslip_search_ids

    def _get_total_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        contract_obj = self.pool.get('hr.contract')
        resource_obj = self.pool.get('resource.calendar')
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        for payslip in self.browse(cr, uid, ids, context=context):
            
            total_timesheet_hours = 0.0
            if payslip.employee_id.user_id:
                timesheet_search_ids = timesheet_obj.search(cr, uid, [('user_id', '=', payslip.employee_id.user_id.id), 
                                               ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to)])
                if timesheet_search_ids:
                    for timesheet in timesheet_obj.browse(cr, uid, timesheet_search_ids, context=context):
                        total_timesheet_hours = total_timesheet_hours + timesheet.unit_amount or 0.0

            total_hours = 0.0
            if payslip.contract_id:
                contact_brw = contract_obj.browse(cr, uid, payslip.contract_id.id, context=context)
                if contact_brw.working_hours:
                    total_hours = resource_obj.get_working_hours(cr, uid, contact_brw.working_hours.id, 
                                 start_dt=datetime.strptime(payslip.date_from, '%Y-%m-%d'), 
                                 end_dt=datetime.strptime(payslip.date_to, '%Y-%m-%d'), 
                                 compute_leaves=True, resource_id=None, default_interval=None, context=context)

            total_overtime = 0.0
            if total_timesheet_hours > total_hours:
                total_overtime = total_timesheet_hours - total_hours

            res.update({payslip.id: {
                            'total_timesheet_hours':total_timesheet_hours,
                            'total_hours': total_hours,
                            'overtime_hours': total_overtime}})
        return res

    def _get_total_public_holiday_hours(self, cr, uid, ids, name, args, context=None):
        res = {}
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        pub_holiday_lines_obj = self.pool.get('hr.holiday.lines')
        for payslip in self.browse(cr, uid, ids, context=context):
            public_holi_ids = pub_holiday_lines_obj.search(cr, uid, [('holiday_date', '>=', payslip.date_from),
                                                                     ('holiday_date', '<=', payslip.date_to),
                                                                     ('holiday_id.state', '=', 'validated')])
            pub_holi_days = []
            for line in pub_holiday_lines_obj.browse(cr, uid, public_holi_ids, context=context):
                pub_holi_days.append(line.holiday_date)
            total_hours = 0.0
            if pub_holi_days and payslip.employee_id.user_id:
                timesheet_search_ids = timesheet_obj.search(cr, uid, [('user_id', '=', payslip.employee_id.user_id.id), 
                                               ('date', '>=', payslip.date_from),
                                               ('date', '<=', payslip.date_to),
                                               ('date', 'in', pub_holi_days)])
                if timesheet_search_ids:
                    for timesheet in timesheet_obj.browse(cr, uid, timesheet_search_ids, context=context):
                        total_hours = total_hours + timesheet.unit_amount or 0.0
            res[payslip.id] = total_hours
        return res

    _columns = {
        'cheque_number':fields.char("Cheque Number", size=64),
        'active': fields.boolean('Pay'),
        'pay_by_cheque': fields.boolean('Pay By Cheque'),
        'employee_name': fields.related('employee_id', 'name', type="char", size=256, string="Employee Name", store=True),
        'active_employee': fields.related('employee_id', 'active', type="boolean", string="Active Employee"),
        'total_timesheet_hours': fields.function(_get_total_hours, store={
                            'hr.payslip': (lambda self, cr, uid, ids, context: ids, [], 10),
                            'hr.analytic.timesheet': (_get_hr_analytic_timesheet_ids, [], 20),
                        }, multi="all", string='Total Timesheet Hours', type='float'),
        'total_hours': fields.function(_get_total_hours, store={
                            'hr.payslip': (lambda self, cr, uid, ids, context: ids, [], 10),
                            'hr.analytic.timesheet': (_get_hr_analytic_timesheet_ids, [], 20),
                        }, multi="all", string='Total Hours', type='float'),
        'overtime_hours': fields.function(_get_total_hours,store={
                            'hr.payslip': (lambda self, cr, uid, ids, context: ids, [], 10),
                            'hr.analytic.timesheet': (_get_hr_analytic_timesheet_ids, [], 20),
                        }, multi="all", string='Overtime Hours', type='float'),
        'pub_holiday_hours': fields.function(_get_total_public_holiday_hours, method=True, string='Public Holiday Hours', type='float'),
        'date': fields.date(string="Payment Date"),
    }

    _defaults = {
        'active': True,
    }

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id, contract_id):
        empolyee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        worked_days_obj = self.env['hr.payslip.worked_days']
        input_obj = self.env['hr.payslip.input']
        period_start_date = date_from
        period_end_date = date_to
        #delete old worked days lines
        old_worked_days_ids = []
        if self.id :
            old_worked_days_ids = [worked_days_rec.id for  worked_days_rec in worked_days_obj.search([('payslip_id', '=', self.id)])]
        if old_worked_days_ids:
            self._cr.execute(""" delete from hr_payslip_worked_days where id in %s""",(tuple(old_worked_days_ids),))
#            worked_days_obj.unlink(self._cr,self._uid,old_worked_days_ids)

        #delete old input lines
        old_input_ids = []
        if self.id :
            old_input_ids = [input_rec.id for input_rec in input_obj.search([('payslip_id', '=', self.id)])]
        if old_input_ids:
            self._cr.execute(""" delete from hr_payslip_input where id in %s""",(tuple(old_input_ids),))
#            input_obj.unlink(old_input_ids)
        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        employeee_id = empolyee_obj.browse(employee_id)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employeee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employeee_id.company_id.id
        })

        if not self._context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(employeee_id, date_from, date_to, context=self._context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employeee_id, date_from, date_to, context=self._context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(contract_ids[0])
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to, context=self._context)
        input_line_ids = self.get_inputs(contract_ids, date_from, date_to, context=self._context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        if not employee_id:
            return res
        active_employee = empolyee_obj.browse(employee_id).active
        res['value'].update({'active_employee': active_employee})
        res['value'].update({'employee_id': employee_id, 'date_from': date_from, 'date_to': date_to})
        if date_from and date_to:
            current_date_from = date_from
            current_date_to = date_to
            date_from_cur = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            previous_month_obj = parser.parse(date_from_cur.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
            total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
            first_day_of_previous_month = datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            last_day_of_previous_month = datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            date_from = datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(date_from), until=parser.parse(date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            new = {'code':'TTLPREVDAYINMTH','name':'Total number of days for previous month','number_of_days':len(dates), 'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVSUNINMONTH','name':'Total sundays in previous month','number_of_days':sunday, 'sequence': 3, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVSATINMONTH','name':'Total saturdays in previous month','number_of_days':saturday, 'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLPREVWKDAYINMTH','name':'Total weekdays in previous month','number_of_days':weekdays, 'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)

            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(current_date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            new = {'code':'TTLCURRDAYINMTH','name':'Total number of days for current month','number_of_days':len(dates), 'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRSUNINMONTH','name':'Total sundays in current month','number_of_days':sunday, 'sequence': 3, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRSATINMONTH','name':'Total saturdays in current month','number_of_days':saturday, 'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code':'TTLCURRWKDAYINMTH','name':'Total weekdays in current month','number_of_days':weekdays, 'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            cur_month_weekdays = 0
            if contract_record:
                contract_start_date = contract_record.date_start
                contract_end_date = contract_record.date_end
                if contract_start_date:
                    if contract_start_date >= current_date_from and contract_start_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(contract_start_date), until=parser.parse(current_date_to)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1
                elif contract_end_date:
                    if contract_end_date >= current_date_from and contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(contract_end_date)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1
            if cur_month_weekdays:
                new = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':cur_month_weekdays, 'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)
            else:
                new = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':weekdays, 'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)

        if employee_id:
            holiday_status_obj = self.env["hr.holidays.status"]
            holiday_status_ids = holiday_status_obj.search([])
            for holiday_status in holiday_status_ids:
                flag = False
                for payslip_data in res["value"].get("worked_days_line_ids"):
                    if payslip_data.get("code") == holiday_status.name:
                        flag = True
                if not flag:
                    new = {'code':holiday_status.name, 'name':holiday_status.name, 'number_of_days':0.0, 'sequence': 0, 'contract_id': contract_record.id}
                    res.get('value').get('worked_days_line_ids').append(new)
        return res

    def compute_sheet(self, cr, uid, ids, context=None):
        result = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        slip_line_pool = self.pool.get('hr.payslip.line')
        lines = []
        for payslip in self.browse(cr, uid, ids, context=context):
            for line in payslip.line_ids:
                if line.amount == 0:
                    lines.append(line.id)
        if lines:
            slip_line_pool.unlink(cr, uid, lines, context=context)
        return result

class hr_employee(osv.Model):
    _inherit = 'hr.employee'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
            Override Search method for put filter on current working status. 
        """
        if context and context.get('batch_start_date') and context.get('batch_end_date'):
            contract_obj = self.pool.get('hr.contract')
            active_contract_employee_list = []
            contract_ids = contract_obj.search(cr, uid, ['|', ('date_end', '>=', context.get('batch_start_date')), ('date_end', '=', False), ('date_start', '<=', context.get('batch_end_date'))])
            for contract in contract_obj.browse(cr, uid, contract_ids):
                active_contract_employee_list.append(contract.employee_id.id)
            args.append(('id', 'in', active_contract_employee_list))
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context=context, count=count)

    _columns = {
            'cessation_date': fields.date('Cessation Date'),
            'identification_no': fields.selection([('1', 'NRIC'), ('2', 'FIN'), ('3', 'Immigration File Ref No.'),
                                                   ('4', 'Work Permit No'), ('5', 'Malaysian I/C (for non-resident director and seaman only)'),
                                                   ('6', 'Passport No. (for non-resident director and seaman only)')], string='2. ID Type of Employee'),
            'address_type': fields.selection([('L', 'Local residential address'),
                                              ('F', 'Foreign address'),
                                              ('C', 'Local C/O address'),
                                              ('N', 'Not Available')], string='Address Type'),
            'empcountry_id': fields.many2one('employee.country', '6(k). Country Code of address'),
            'empnationality_id': fields.many2one('employee.nationality', '7. Nationality Code'),
            'cessation_provisions': fields.selection([('Y', 'Cessation Provisions applicable'),
                                                      ('N', 'Cessation Provisions not applicable')], string='28. Cessation Provisions'),
            'employee_type' : fields.selection([('full_employeement', 'Full Employer & Graduated Employee (F/G)'),
                                                      ('graduated_employee', 'Graduated Employer & Employee (G/G)')], string='Employee Type'),
    }

    _defaults = {
            'employee_type' : 'full_employeement'
    }

class employee_country(osv.Model):
    _name = 'employee.country'
    _columns = {
            'name': fields.char('Country', size=32, required=True),
            'code': fields.integer('Code', size=3, required=True)
    }

class employee_nationality(osv.Model):
    _name = 'employee.nationality'
    _columns = {
            'name': fields.char('Nationality', size=32, required=True),
            'code': fields.integer('Code', size=3, required=True)
    }

class hr_payslip_run(osv.Model):

    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    def open_payslip_employee(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        payslip_batch_data = self.browse(cr, uid, ids[0], context)
        context.update({'default_date_start': payslip_batch_data.date_start, 'default_date_end': payslip_batch_data.date_end})
        return {'name': ('Payslips by Employees'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.payslip.employees',
                'type': 'ir.actions.act_window',
                'target': 'new',
        }

class hr_payslip_employees(osv.TransientModel):
    _inherit = 'hr.payslip.employees'

    _columns = {
        'date_start': fields.date('Date From'),
        'date_end': fields.date('Date To'),
    }

class res_users(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'user_ids': fields.many2many('res.users', 'ppd_res_user_payroll_rel','usr_id','user_id','User Name'),
    }

class res_company(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'company_code': fields.char('Company Code')
    }

class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
        'level_no': fields.char('Level No'),
        'house_no': fields.char('House No'),
        'unit_no': fields.char('Unit No'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: