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

    def _get_codes(self, based_on, company_id,tax_chart_id,parent=False, level=0, period_list=None, context=None):
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
        res = []
        sum_pr=0
        if full_year==None:
            start_period=period_list[0]
            end_period=period_list[-1]
            period_list=[]
            while start_period!=end_period+1:
                period_list.append(start_period)
                start_period+=1
            
        obj_tc = self.pool.get('account.tax.code')
        for account in account_list:
            ids = obj_tc.search(self.cr, self.uid, [('id', '=', account[1].id)], context=context)
            sum_tax_add = 0    
            for period_ind in period_list:
                for code in obj_tc.browse(self.cr, self.uid, ids, {'period_id':period_ind, 'based_on': based_on}):
                    sum_tax_add = sum_tax_add + code.sum_period
                    code.sum_period = sum_tax_add
                    sum_pr=code.sum_period
            res.append((account[0], code,sum_pr))
        return res

    def get_info(self, form, context=None):
        if context == None:
            context = {}
        tax_list = []
        obj_tax_code = self.pool.get('account.tax.code')
        account_template_obj = self.pool.get('account.account')
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id
        account_template_id = account_template_obj.search(self.cr, self.uid,[('company_id','=',company_id.id),('code', '=','4100')])
        period_list = []
        ctx = context.copy()
       # ctx.update({'period_id': form['period_to'][0]})
        if form['tax_chart_id']:
            res = self._get_codes('invoices', company_id.id,form['tax_chart_id'][0],False, 0, period_list, context)
        else:
            res = self._get_codes('invoices', company_id.id,False,False, 0, period_list, context)
        
        if form['period_from'] and form['period_to']:
            if form['period_from'][0]==form['period_to'][0]:
                period_list.append(form['period_from'][0])
            else:
                period_list.append(form['period_from'][0])
                period_list.append(form['period_to'][0])
            res = self._add_codes('invoices', res, period_list, context=context)
        elif form['period_from']:
            period_list.append(form['period_from'][0])
            res = self._add_codes('invoices', res, period_list, context=context)
        elif form['period_to']:
            period_list.append(form['period_to'][0])
            res = self._add_codes('invoices', res, period_list, context=context)
        else:
            self.cr.execute ("select id from account_fiscalyear")
            fy = self.cr.fetchall()
            self.cr.execute ("select id from account_period where fiscalyear_id = %s", (fy[0][0],))
            periods = self.cr.fetchall()
            for p in periods:
                period_list.append(p[0])
            full_year=True    
            res = self._add_codes('invoices', res, period_list,full_year, context=context)
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
            if tax[1].code in ['SRB','DSB']:
                box1 += tax[2]
                box4 += tax[2]
            if tax[1].code == 'ZRB':
                box2 = tax[2]
                box4 += tax[2]
            if tax[1].code in ['ES33B','ESN33B']:
                box3 += tax[2]
                box4 += tax[2]
            if tax[1].code in ['TXB', 'ZPB', 'IMB', 'MEB', 'IGDSB']:
                box5 += tax[2]
            if tax[1].code in ['SR', 'DS']:
                box6 += tax[2]
            if tax[1].code in ['TX', 'ZR', 'IM', 'ME', 'IGDS']:
                box7 += tax[2]
            if tax[1].code == 'MEB':
                box9 = tax[2]
        box7 += box10 + box11
        box8 = box6 - box7
        if account_template_id:
            template_info = account_template_obj.browse(self.cr, self.uid, account_template_id[0])
            box13 = template_info.balance
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
    
report_sxw.report_sxw('report.gstreturn', 'account.tax.code',
    'addons/sg_account/report/gst_return_report.rml', parser=report_gst_return, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
