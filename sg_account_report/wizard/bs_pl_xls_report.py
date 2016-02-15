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
import openerp.tools
from openerp.tools.translate import _
import base64
import xlwt
from cStringIO import StringIO
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import locale
import openerp.tools
from openerp.addons.sg_account_report.report.financial_report import account_balance_inherit

class bs_pl_xls_report(osv.osv_memory):
    _name = "bs.pl.xls.report"
    
    def _get_excel_export_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        bank_obj = self.pool.get('hr.bank.details')
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        header2 = xlwt.easyxf('font: bold 1, height 180')
        header1 = xlwt.easyxf('pattern: pattern solid, fore_colour white; borders: top double, bottom double, bottom_color black; font: bold on, height 180, color black; align: wrap off')
        company_name = self.pool.get('res.users').browse(cr, uid, uid).company_id.name
        account_balance_inherit_obj = account_balance_inherit(cr, uid, '', context)
        acc_data = account_balance_inherit_obj.lines(context.get('form'), 0)
        style = xlwt.easyxf('align: wrap yes')
        worksheet.col(0).width = 15000
        worksheet.col(1).width = 5000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.row(2).height = 500
        row = 6
        if context.get('inf_type') == 'BS':
            worksheet.write(0, 1, company_name , header)
            worksheet.write(1, 1, 'Balance Sheet' , header)
            worksheet.write(2, 1, 'As of ' + datetime.date.today().strftime('%m') + ' ' + context['form'].get('fiscalyear')[1] , header)
        if context.get('inf_type') == 'IS':
            worksheet.write(0, 1, company_name , header)
            worksheet.write(1, 1, 'Profit Loss' , header)
            worksheet.write(2, 1, context['form'].get('period_id')[1] , header)
            worksheet.write(3, 3, 'Current Month' , header2)
            worksheet.write(3, 4, 'Year to Date' , header2)
            worksheet.write(4, 3, 'Amount' , style)
            worksheet.write(4, 4, 'Amount' , style)
        for acc in acc_data:
            if context.get('inf_type') == 'BS':
                if acc['type']=='view' and acc['name'] or acc['name'].title():
                    if acc['total'] and not acc['label']:
                        worksheet.write(row, 0,'    '*(acc['level']-1) + acc['name'],header1)
                        worksheet.write(row, 1,'',header1)
                        worksheet.write(row, 2,'',header1)
                    else:
                        worksheet.write(row, 0,'    '*(acc['level']-1) + acc['name'],style)
                if acc['total']==True:
                    if acc['total'] and not acc['label']:
                        worksheet.write(row, 3, round(acc['balance'] or 0.00 , 2),header1)
                    else:
                        worksheet.write(row, 3, round(acc['balance'] or 0.00, 2),style)
                row += 1
            if context.get('inf_type') == 'IS':
                if acc['type']=='view' and acc['name'] or acc['name'].title():
                    if acc['total'] and not acc['label']:
                        worksheet.write(row, 0,'    '*(acc['level']-1) + acc['name'],header1)
                        worksheet.write(row, 1,'',header1)
                        worksheet.write(row, 2,'',header1)
                    else:
                        worksheet.write(row, 0,'    '*(acc['level']-1) + acc['name'],style)
                if acc['total']==True:
                    if acc['total'] and not acc['label']:
                        worksheet.write(row, 3, round(abs(acc['month']) or 0.00, 2),header1)
                        worksheet.write(row, 4, round(abs(acc['balance']) or 0.00, 2),header1)
                    else:
                        worksheet.write(row, 3, round(abs(acc['month']) or 0.00, 2),style)
                        worksheet.write(row, 4, round(abs(acc['balance']) or 0.00, 2),style)
                row += 1
        
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle() # Create Style
        border_style.borders = borders
        row = 2
        payslip_obj = self.pool.get('hr.payslip')
        employee_obj = self.pool.get('hr.employee')
        hr_depart_obj = self.pool.get('hr.department')
        new_employee_ids = []
        style = xlwt.easyxf('align: wrap yes',style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)
        
    _columns = {
        "file":fields.binary("Click On Download Link To Download Xls File", readonly=True),
        "name":fields.char("Name" , size=32, invisible="1")
    }
    
    _defaults = {
        'name':"BS PL.xls",
        'file': _get_excel_export_data
    }

bs_pl_xls_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: