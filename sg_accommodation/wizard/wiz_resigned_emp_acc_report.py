from openerp import fields, models, api, _
from pytz import timezone
from datetime import date, timedelta, datetime, tzinfo
from dateutil import parser
from dateutil.relativedelta import relativedelta
import tempfile
import xlwt
from xlwt import Workbook
from StringIO import StringIO
import base64
import time
from pytz import timezone
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,misc,DEFAULT_SERVER_DATETIME_FORMAT

class acc_report_resigned_emp(models.TransientModel):
    
    _name = 'acc.report.resigned.emp'
    
    start_month = fields.Many2one('account.period','Start Month')
    end_month = fields.Many2one('account.period','End Month')
    company_id=fields.Many2one('res.company','Company Id')
    
    _defaults = {
         'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'acc.report.resigned.emp', context=c)
    }
    @api.multi
    def print_report(self):
        emp_obj = self.env['hr.employee']
        bed_obj = self.env['beds.beds']
        emps = emp_obj.search([('accommodated', '=', True), ('last_date', '>=', self.start_month.date_start), ('last_date', '<=', self.end_month.date_stop)], order='last_date')
        month_list = []
        check_months = []
        for emp in emps:
            ctr = 1
            emp_last_date = datetime.strptime(emp.last_date, DEFAULT_SERVER_DATE_FORMAT)
            month = emp_last_date.strftime('%B-%Y')
            bed = bed_obj.search([('employee_id', '=', emp.id)])
            if bed:
                emp_dict = {
                    'sr':ctr or '',
                    'emp_id':emp.identification_id or '',
                    'name':emp.name or '',
                    'wp_number':emp.wp_number or '',
                    'company':emp.company_id and emp.company_id.code or '',
                    'dialect':emp.dialect or '',
                    'site':emp.worker_location_id and emp.worker_location_id.name or '',
                    'app_date':emp.app_date or '',
                    'last_date':emp.last_date or '',
                    'accommodation':bed.room_id and bed.room_id.accommodation_id and bed.room_id.accommodation_id.name or '',
                    'print_emp' : True,
                    }
                ctr += 1
                
                if month_list:
                    check_months = [m for m, dict2 in month_list]
                    month_index_dict = dict([(m2, month_list.index((m2, dict2))) for m2, dict2 in month_list])
                if month.upper() in check_months:
                    month_list[month_index_dict[month.upper()]][1].append(emp_dict)
                else:
                    month_list.append((month.upper(), [emp_dict]))
                    
        fl = StringIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        for_left = xlwt.easyxf("font: color black; align: horiz left")
        for_center_bold = xlwt.easyxf("font: bold 1, color black; align: horiz center")
#         for_center = xlwt.easyxf("font: bold 1, color black; align: horiz center; pattern: fore_colour red;")

        GREEN_TABLE_HEADER = xlwt.easyxf(
                 'font: bold 1, name Tahoma, height 250;'
                 'align: vertical center, horizontal center, wrap on;'
#                  'borders: left thin, right thin, top thin, bottom thin;'
                 'borders: top double, bottom double, left double, right double;'
                 'pattern: pattern solid, pattern_fore_colour white, pattern_back_colour white'
                 )
        
        BLACK_MONTH_HEADER = xlwt.easyxf(
                 'font: bold 1, color white, name Tahoma, height 160;'
                 'align: vertical center, horizontal center, wrap on;'
                 'borders: left thin, right thin, top thin, bottom thin;'
                 'pattern: pattern solid, pattern_fore_colour black, pattern_back_colour black'
                 )
        
        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'
        
        worksheet.row(0).height = 320
        worksheet.col(0).width = 4000
        worksheet.col(1).width = 4000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.col(6).width = 6000
        worksheet.col(7).width = 4000
        worksheet.col(8).width = 4000
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        
        worksheet.write_merge(0, 0, 0, 8, 'RESIGNED WORKERS',GREEN_TABLE_HEADER)
        worksheet.write(1, 0, 'CODE NO', for_center_bold)
        worksheet.write(1, 1, 'NAME', for_center_bold)
        worksheet.write(1, 2, 'W/P NUMBER', for_center_bold)
        worksheet.write(1, 3, 'COM', for_center_bold)
        worksheet.write(1, 4, 'DIALECT', for_center_bold)
        worksheet.write(1, 5, 'SITE', for_center_bold)
        worksheet.write(1, 6, 'DATE OF APPLICATION', for_center_bold)
        worksheet.write(1, 7, 'DEPARTURE DT', for_center_bold)
        worksheet.write(1, 8, 'ACCOM', for_center_bold)
        if month_list:
            row = 2
            col1 = 0
            col = 8
            for month, month_data in month_list:
                worksheet.write_merge(row, row, col1, col, month,BLACK_MONTH_HEADER)
                if month_data:
                    row = row + 1
                    for month_dict in month_data:
                        worksheet.write(row, 0, month_dict.get('emp_id'), for_left)
                        worksheet.write(row, 1, month_dict.get('name'), for_left)
                        worksheet.write(row, 2, month_dict.get('wp_number'), for_left)
                        worksheet.write(row, 3, month_dict.get('company'), for_left)
                        worksheet.write(row, 4, month_dict.get('dialect'), for_left)
                        worksheet.write(row, 5, month_dict.get('site'), for_left)
                        worksheet.write(row, 6, month_dict.get('app_date'), for_left)
                        worksheet.write(row, 7, month_dict.get('last_date'), for_left)
                        worksheet.write(row, 8, month_dict.get('accommodation'), for_left)
#                         worksheet.write(row, 9, month_dict.get('print_emp',''), for_left)
                        row = row + 1
                    
        workbook.save(fl)
        fl.seek(0)
        
        buf = base64.encodestring(fl.read())
        cr, uid, context = self.env.args
        ctx = dict(context)
        ctx.update({'file': buf})
        self.env.args = cr, uid, misc.frozendict(context)
                    
#         datas = {
#             'ids' : [],
#             'model' : 'acc.report.resigned.emp',
#             'form': month_list,
#             }
#         return {'type': 'ir.actions.report.xml',
#                 'report_name': 'acc.report.resigned.emp.doc',
#                 'datas': datas
#                 }
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'acc.report.resigned.emp.standard.export',
                'target': 'new',
                'context': ctx,
        }
    
class acc_report_resigned_emp_standard_export(models.TransientModel):
    
    _name = 'acc.report.resigned.emp.standard.export'
        
    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
            
        context = self._context
        res = super(acc_report_resigned_emp_standard_export, self).default_get(fields)
        res.update({'name': 'Resigned Employee.xls'})
        if self._context.get('file'):
            res.update({'file': context['file']})
        return res

    file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    @api.multi
    def action_back(self):
        if self._context is None:
            self._context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acc.report.resigned.emp',
            'target': 'new',
        }
    

