# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
import xlwt
import time
from cStringIO import StringIO
from openerp.addons.sg_account_report.report.trial_balance import account_balance

class excel_export_trial(osv.osv_memory):
    _name = "excel.export.trial"
    
    _columns = {
        "file":fields.binary("Click On Download Link To Download Xls File", readonly=True),
        "name":fields.char("Name" , size=32)
    }
    
    def _get_excel_trial_data(self, cr, uid, context=None):
    	period_name = context.get('period_id')
    	workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        bottomheader = xlwt.easyxf('font: bold 1, height 200')
        header1 = xlwt.easyxf('pattern: pattern solid, fore_colour white; borders: top double, bottom double, bottom_color black; font: bold on, height 180, color black; align: wrap off')
        style = xlwt.easyxf('font: height 180')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.row(2).height = 500
        company_name = self.pool.get('res.users').browse(cr, uid, uid).company_id.name
        worksheet.write(0, 1, company_name , header)
        worksheet.write(1, 1, period_name , header)
        worksheet.write(2, 1, "Trial Balance" , header)
        worksheet.write(4, 0, "Account" , header1)
        worksheet.write(4, 1, "" , header1)
        worksheet.write(4, 2, "Debit" , header1)
        worksheet.write(4, 3, "Credit" , header1)
        worksheet.write(4, 4, "YTD Debit" , header1)
        worksheet.write(4, 5, "YTD Credit" , header1)
        row = 5
        context['form'].update({'fiscalyear_id':context['form']['fiscalyear_id'][0]})
        account_balance_inherit_obj = account_balance(cr, uid, '', context)
        acc_data = account_balance_inherit_obj.lines(context.get('form'), [1], None)
        tot_deb = tot_cre = tot_ytd_deb = tot_ytd_cre = 0.00
        for acc in acc_data:
            worksheet.write(row, 0, acc['name'] , style)
            worksheet.write(row, 2, round(acc['debit'] or 0.00, 2) , style)
            worksheet.write(row, 3, round(acc['credit'] or 0.00, 2) , style)
            worksheet.write(row, 4, round(acc['ytd_debit'] or 0.00, 2) , style)
            worksheet.write(row, 5, round(acc['ytd_credit'] or 0.00, 2) , style)
            tot_deb += acc['debit']
            tot_cre += acc['credit']
            tot_ytd_deb += acc['ytd_debit']
            tot_ytd_cre += acc['ytd_credit']
            row += 1
        row += 2
        worksheet.write(row, 0, 'Total' , header1)
        worksheet.write(row, 1, "" , header1)
        worksheet.write(row, 2, round(tot_deb or 0.00, 2) , header1)
        worksheet.write(row, 3, round(tot_cre or 0.00, 2) , header1)
        worksheet.write(row, 4, round(tot_ytd_deb or 0.00, 2) , header1)
        worksheet.write(row, 5, round(tot_ytd_cre or 0.00, 2) , header1)
        row += 2
        worksheet.write(row, 0, 'Difference' , header1)
        worksheet.write(row, 1, "" , header1)
        worksheet.write(row, 2, "" , header1)
        worksheet.write(row, 3, round(tot_deb - tot_cre or 0.00, 2) , header1)
        worksheet.write(row, 4, "" , header1)
        worksheet.write(row, 5, round(tot_ytd_deb - tot_ytd_cre or 0.00, 2) , header1)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)

    _defaults = {
        'name':"Export_Trial.xls",
        'file': _get_excel_trial_data
    }


class trial_balance_wiz(osv.osv_memory):
    _inherit = 'account.balance.report'
    _description = 'Trial Balance Report'

    _columns = {
        'period_id': fields.many2one('account.period', 'Period')
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_id'], context=context)[0])
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.trial.balance', 'datas': data}

    def get_trial_data(self,cr,uid,ids,context=None):
        data = self.read(cr, uid, ids)[0]
        period_data = self.pool.get('account.period').browse(cr, uid, data['period_id'][0], context=context)
        account_obj = self.pool.get('account.account')
        account_data = account_obj.browse(cr, uid, data['chart_account_id'][0], context=context)
        fiscalyear_data = account_obj.browse(cr, uid, data['fiscalyear_id'][0], context=context)
        context.update({'form':data, 'period_id':period_data.name,'company_name':account_data.company_id.name, 'fiscalyear':fiscalyear_data.name,'date_from':period_data.date_start,'date_to':period_data.date_stop})
        return {
          'name': _('Binary'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'excel.export.trial',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: