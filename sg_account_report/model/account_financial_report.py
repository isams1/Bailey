# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Serpent Consulting Services (<http://serpentcs.com>).
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
from openerp import pooler
import time
from openerp.tools.translate import _
from openerp.tools import frozendict

class account_financial_report(osv.Model):
    _name = "afr"

    _columns = {
        'name': fields.char('Name', size= 128, help="""This will be the title that will be displayed in the header of the report. E.g. - "Balance Sheet" or "Income Statement".""", required=True),
        'company_id': fields.many2one('res.company','Company',required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', help="This will be the currency in which the report will be stated in. If no currency is selected, the default currency of the company will be selected."),
        'inf_type': fields.selection([('BS','Balance Sheet'),('IS','Income Statement'),('TB', 'Trial Balance'),('GL', 'General Ledger')],'Type',required=True),
        'columns': fields.selection([('one','End. Balance'),('two','Debit | Credit'), ('four','Initial | Debit | Credit | YTD'), ('five','Initial | Debit | Credit | Period | YTD'),('qtr',"4 QTR's | YTD"),('thirteen','12 Months | YTD')],'Columns',required=True),
        'display_account': fields.selection([('all','All Accounts'),('bal', 'With Balance'),('mov','With movements'),('bal_mov','With Balance / Movements')],'Display Accounts'),
        'display_account_level': fields.integer('Up To Level',help='Display accounts up to this level (0 to show all)'),
        'account_ids': fields.many2many ('account.account','afr_account_rel','afr_id','account_id','Root accounts',required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear','Fiscal Year', required=True),
        'period_ids': fields.many2many('account.period','afr_period_rel','afr_id','period_id','Periods'),
        'analytic_ledger': fields.boolean('Analytic Ledger', help="""You can generate a "Transactions by GL Account" report if you click this check box. Make sure to select "Balance Sheet" and "Initial | Debit | Credit | YTD" in their respective fields."""),
        'tot_check': fields.boolean('Ending Total for Financial Statements ?', help='Please check this box if you would like to get an accumulated amount for each column (Period, Quarter, or Year) at the bottom of this report.'),
        'lab_str': fields.char('Description for Ending Total', help="""E.g. - Net Income (Loss)""", size= 128),
        'user_id' : fields.many2one("res.users","Current Logged in user"),
        #~ Deprecated fields
        'filter': fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')],'Date/Period Filter'),
        'date_to': fields.date('End Date'),
        'date_from': fields.date('Start Date'),
    }

    _defaults = {
        'display_account_level': lambda *a: 0,
        'inf_type': lambda *a:'BS',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
        'fiscalyear_id': lambda self, cr, uid, c: self.pool.get('account.fiscalyear').find(cr, uid),
        'display_account': lambda *a:'bal_mov',
        'columns': lambda *a:'five',
        
        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'filter': lambda *a:'byperiod',
        'user_id':lambda self,cr,uid,context: uid,
    }
    
    def copy(self, cr, uid, id, defaults, context=None):
        if context is None:
            context = {}
        previous_name = self.browse(cr, uid, id, context=context).name
        new_name = _('Copy of %s')%previous_name
        lst = self.search(cr, uid, [('name','like',new_name)], context=context)
        if lst:
            new_name = '%s (%s)' % (new_name, len(lst)+1)
        defaults['name'] = new_name
        return super(account_financial_report,self).copy(cr, uid, id, defaults, context=context)

    def onchange_inf_type(self,cr,uid,ids,inf_type,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if inf_type != 'BS':
            res['value'].update({'analytic_ledger':False})
        return res

    def onchange_columns(self,cr,uid,ids,columns,fiscalyear_id,period_ids,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if columns != 'four':
            res['value'].update({'analytic_ledger':False})
        if columns in ('qtr', 'thirteen'):
            p_obj = self.pool.get("account.period")
            period_ids = p_obj.search(cr,uid,[('fiscalyear_id','=',fiscalyear_id),('special','=',False)],context=context)
            res['value'].update({'period_ids':period_ids})
        else:
            res['value'].update({'period_ids':[]})
        return res
        
    def onchange_analytic_ledger(self,cr,uid,ids,company_id,analytic_ledger,context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if isinstance(ctx, frozendict):
            ctx = dict(ctx)
        ctx['company_id']=company_id
        res = {'value':{}}
        cur_id = self.pool.get('res.company').browse(cr,uid,company_id,context=ctx).currency_id.id
        res['value'].update({'currency_id':cur_id})
        return res
        
    def onchange_company_id(self,cr,uid,ids,company_id,context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if isinstance(ctx, frozendict):
            ctx = dict(ctx)
        ctx['company_id']=company_id
        res = {'value':{}}
        if not company_id:
            return res
        cur_id = self.pool.get('res.company').browse(cr,uid,company_id,context=ctx).currency_id.id
        fy_id = self.pool.get('account.fiscalyear').find(cr, uid,context=ctx)
        res['value'].update({'fiscalyear_id':fy_id})
        res['value'].update({'currency_id':cur_id})
        res['value'].update({'account_ids':[]})
        res['value'].update({'period_ids':[]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: