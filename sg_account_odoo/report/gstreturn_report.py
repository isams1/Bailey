# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2012 OpenERP SA (<http://www.serpentcs.com>)
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

class report_gst_return(report_sxw.rml_parse):
    _name = 'report.gst.return'

    def __init__(self, cr, uid, name, context=None):
        super(report_gst_return, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_codes': self._get_codes,
            'get_info': self.get_info,
        })

    def _get_codes(self, based_on, company_id, tax_chart_id, parent=False, level=0, period_list=None, context=None):
        obj_tc = self.pool.get('account.tax.code')
        if tax_chart_id!=False:
            ids = obj_tc.search(self.cr, self.uid, [('parent_id', 'child_of',tax_chart_id),('parent_id', '=', parent), ('company_id', '=', company_id)], order='sequence', context=context)
        else:
            ids = obj_tc.search(self.cr, self.uid, [('parent_id', '=', parent), ('company_id', '=', company_id)], order='sequence', context=context)
        res = []
        for code in obj_tc.browse(self.cr, self.uid, ids, {'based_on': based_on}):
            res.append(('.' * 2 * level, code))
            res += self._get_codes(based_on, company_id,tax_chart_id,code.id, level + 1, context=context)
        return res

    def _add_codes(self, based_on, account_list=None, period_list=None,full_year=None, context=None):
        if account_list is None:
            account_list = []
        if period_list is None:
            period_list = []
        if context is None:
            context = {}
        ctx = context.copy()
        cr = self.cr
        uid = self.uid
        tax_code_obj = self.pool.get('account.tax.code')
        period_obj = self.pool.get('account.period')
        start_dt = ''
        end_dt = ''
        period_lst_ids = period_list
        res = []
        if len(period_list) == 2:
            period_list.sort()
            start_dt = period_obj.browse(cr, uid, period_list[0]).date_start
            end_dt = period_obj.browse(cr, uid, period_list[1]).date_stop
        elif len(period_list) == 1:
            start_dt = period_obj.browse(cr, uid, period_list[0]).date_start
            end_dt = period_obj.browse(cr, uid, period_list[0]).date_stop
        if len(period_list) == 2 or len(period_list) == 1:
            period_lst_ids = period_obj.search(cr, uid, [('date_start','>=', start_dt),('date_stop','<=', end_dt)], context=ctx)
        for account in account_list:
            sum_tax_add = 0
            tot_period_sum = 0.0
            period_lst = []
            for period_id in period_lst_ids:
                if period_id not in period_lst:
                    period_lst.append(period_id)
                else:
                    break
                ctx.update({'period_id':period_id, 'based_on': based_on})
                for code in tax_code_obj.browse(cr, uid, [account[1].id], context=ctx):
                    sum_tax_add = sum_tax_add + code.sum_period
#                    code.sum_period = sum_tax_add
                    sum_pr = code.sum_period
                res.append((account[0], code))
#                res.append((account[0], code))
        return res

    def get_info(self, form, context=None):
        if context == None:
            context = {}
        tax_list = []
        period_list = []
        cr = self.cr
        uid = self.uid
        ctx = context.copy()
        obj_tax_code = self.pool.get('account.tax.code')
        account_obj = self.pool.get('account.account')
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id
        account_ids = account_obj.search(self.cr, self.uid,[('company_id','=',company_id.id),('name', '=','Revenue')])
       # ctx.update({'period_id': form['period_to'][0]})
        if form['tax_chart_id']:
            res = self._get_codes('invoices', company_id.id,form['tax_chart_id'][0],False, 0, period_list, context)
        else:
            res = self._get_codes('invoices', company_id.id, False, False, 0, period_list, context)
        period_from = form.get('period_from', False) or False
        period_to = form.get('period_to', False) or False
        fiscalyear_id = form.get('fiscalyear_id',False)[0] or False
        if period_from and period_to:
            if period_from[0] == period_to[0]:
                period_list.append(period_from[0])
            else:
                period_list.append(period_from[0])
                period_list.append(period_to[0])
            res = self._add_codes('invoices', res, period_list, context=context)
            ctx.update({'period_from': period_from[0], 'period_to': period_to[0]})
        elif period_from:
            period_list.append(period_from[0])
            res = self._add_codes('invoices', res, period_list, context=context)
            ctx.update({'period_from': period_from[0], 'period_to': period_from[0]})
        elif period_to:
            period_list.append(period_to[0])
            res = self._add_codes('invoices', res, period_list, context=context)
            ctx.update({'period_from': period_to[0], 'period_to': period_to[0]})
        else:
            self.cr.execute("select id from account_fiscalyear where id = %s", (tuple([fiscalyear_id])))
            fy = self.cr.fetchall()
            self.cr.execute("select id from account_period where fiscalyear_id = %s", (fy[0][0],))
            periods = self.cr.fetchall()
            for p in periods:
                period_list.append(p[0])
            full_year = True
            res = self._add_codes('invoices', res, period_list, full_year, context=context)
            fiscalyear_rec = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=ctx)
            start_date = fiscalyear_rec.date_start or False
            end_date = fiscalyear_rec.date_stop or False
            period_ids = self.pool.get('account.period').search(cr, uid, [('date_start','>=', start_date),('date_stop','<=', end_date)], 
                                                         order='date_start asc, date_stop asc')
            if len(period_ids) == 13: 
                ctx.update({'period_from': period_ids[1],'period_to': period_ids[12]})
        company_name = company_id.name
        tax_no = company_id.vat
        gst_no = company_id.gst_no
        period = form['fiscalyear_id'][1]
        box1 = box2 = box3 = box4 = box5 = box6 = box7 = box8 = box9 = box10 = box11 = box12 = box13 = 0.00
        box10 = form['box10'] or 0.00
        box11 = form['box11'] or 0.00
        box12 = form['box12'] or 0.00
        tax_dics = {}
        for tax in res:
            if tax[1].code == '[Box 1]':
                box1 += tax[1].sum_period
                box4 += tax[1].sum_period
            if tax[1].code == '[Box 2]':
                box2 += tax[1].sum_period
                box4 += tax[1].sum_period
            if tax[1].code == '[Box 3]':
                box3 += tax[1].sum_period
                box4 += tax[1].sum_period
            if tax[1].code == '[Box 5]':
                box5 += tax[1].sum_period
            if tax[1].code == '[Box 6]':
                box6 += tax[1].sum_period
            if tax[1].code == '[Box 7]':
                box7 += tax[1].sum_period
            if tax[1].code == '[Box 9]':
                box9 = tax[1].sum_period
        box7 += box10 + box11
        box8 = box6 - abs(box7)
        if account_ids:
            account_rec = account_obj.browse(self.cr, self.uid, account_ids[0], context=ctx)
            box13 = abs(account_rec.balance)
        tax_dics.update({
            'name': company_name,
            'tax_no': tax_no,
            'gst_no': gst_no,
            'period': period,
            'box1': box1,
            'box2': box2,
            'box3': box3,
            'box4': box4,
            'box5': box5,
            'box6': box6,
            'box7': box7,
            'box8': box8,
            'box9': box9,
            'box10': box10,
            'box11': box11,
            'box12': box12,
            'box13': box13
        })
        tax_list.append(tax_dics)
        return tax_list
    
report_sxw.report_sxw('report.gstreturn.odoo', 'account.tax.code',
    'addons/sg_account_odoo/report/gst_return_report.rml', parser=report_gst_return, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
