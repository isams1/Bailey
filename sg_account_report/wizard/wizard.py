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

from openerp.osv import osv,fields
from openerp import pooler
import time
from openerp.tools.translate import _

class wizard_report(osv.TransientModel):
    _name = "wizard.report"

    _columns = {
        'afr_id': fields.many2one('afr','Report Template'),
        'company_id': fields.many2one('res.company','Company',required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', help="This will be the currency in which the report will be stated in. If no currency is selected, the default currency of the company will be selected."),
        'inf_type': fields.selection([('BS','Balance Sheet'),('IS','Profit & Loss'), ('TB', 'Trial Balance'),('GL', 'General Ledger')],'Type',required=True),
        'columns': fields.selection([('one','End. Balance'),('two','Debit | Credit'), ('four','Initial | Debit | Credit | YTD'), ('five','Initial | Debit | Credit | Period | YTD'),('qtr',"4 QTR's | YTD"),('thirteen','12 Months | YTD')],'Columns',required=True),
        'display_account': fields.selection([('all','All Accounts'),('bal', 'With Balance'),('mov','With movements'),('bal_mov','With Balance / Movements')],'Display Accounts'),
        'display_account_level': fields.integer('Up To Level',help='Display accounts up to this level (0 to show all)'),
        'account_list': fields.many2many ('account.account','rel_wizard_account','account_list','account_id','Root Accounts',required=True),
        'fiscalyear': fields.many2one('account.fiscalyear','Fiscal Year',help='Fiscal Year for this report',required=True),
#        'period_id' : fields.many2one('account.period', 'Period'),
        'periods': fields.many2many('account.period','rel_wizard_period','wizard_id','period_id','Periods'),
        'org_periods_from':fields.many2one('account.period', 'Start Period'),
        'org_periods_to':fields.many2one('account.period', 'End Period'),
        'analytic_ledger': fields.boolean('Analytic Ledger', help="""You can generate a "Transactions by GL Account" report if you click this check box. Make sure to select "Balance Sheet" and "Initial | Debit | Credit | YTD" in their respective fields."""),
        'tot_check': fields.boolean('Ending Total for Financial Statements?', help='Please check this box if you would like to get an accumulated amount for each column (Period, Quarter, or Year) at the bottom of this report.'),
        'lab_str': fields.char('Description for Ending Total', help="""E.g. - Net Income (Loss)""", size= 128),
        #~ Deprecated fields
        'filter': fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')],'Date/Period Filter',help="If you will select the 'By Date and Period' filter, first it will give preference to periods and then to date range."),
        'date_to': fields.date('End Date'),
        'date_from': fields.date('Start Date'),
        'compr_filter':fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')], 'Filter By'),
        'compr_fiscalyear_id': fields.many2one('account.fiscalyear','Fiscal Year'),
        'compr0_periods_from': fields.many2one('account.period','Start Periods'),
        'compr0_periods_to': fields.many2one('account.period','End Periods'),
        'compr0_filter':fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')], 'Compare By'),
        'compr0_fiscalyear_id': fields.many2one('account.fiscalyear','Fiscal Year'),
        'compr0_date_to': fields.date('End Date'),
        'compr0_date_from': fields.date('Start Date'),
#       'compr0_periods': fields.many2many('account.period','rel_wizard_period_compr0','compr0_wizard_id','period_id','Periods',help='All periods in the fiscal year if empty'),
        'compr1_filter':fields.selection([('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')], 'Compare By'),
        'compr1_fiscalyear_id': fields.many2one('account.fiscalyear','Fiscal Year'),
        'compr1_date_to': fields.date('End Date'),
        'compr1_date_from': fields.date('Start Date'),
        'compr1_periods_from': fields.many2one('account.period','Start Periods'),
        'compr1_periods_to': fields.many2one('account.period','End Periods'),
#       'compr1_periods': fields.many2many('account.period','rel_wizard_period_compr0','compr0_wizard_id','period_id','Periods',help='All periods in the fiscal year if empty'),
        'periodic_columns': fields.selection([('one','End. Balance'),('two','Debit | Credit'), ('four','Initial | Debit | Credit | YTD')],'Columns'),
        'earning_account': fields.many2one('account.account', 'If so, please select a Retained Earnings Acct.'),
        'show_earning': fields.boolean('Is this a Balance Sheet ?'),
    }

    _defaults = {
#        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
#        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        'filter': lambda *a:'none',
        'display_account_level': lambda *a: 0,
        'inf_type': lambda *a:'BS',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
        'fiscalyear': lambda self, cr, uid, c: self.pool.get('account.fiscalyear').find(cr, uid),
        'display_account': lambda *a:'bal_mov',
        'columns': lambda *a:'five',
        'periodic_columns':lambda *a:'one',
    }

    def onchange_inf_type(self,cr,uid,ids,inf_type,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
#        if inf_type == 'BS':
#            res['value'].update({'columns':'one'})
#        if inf_type == 'IS':
#            res['value'].update({'columns':'two'})
#         if inf_type != 'BS':
#             res['value'].update({'analytic_ledger':False})
        return res

    def onchange_columns(self,cr,uid,ids,columns,fiscalyear,periods,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        p_obj = self.pool.get("account.period")
        all_periods = p_obj.search(cr,uid,[('fiscalyear_id','=',fiscalyear),('special','=',False)],context=context)
#         s = set(periods[0][2])
        t = set(all_periods)
#         go = periods[0][2] and s.issubset(t) or False
        if columns != 'four':
            res['value'].update({'analytic_ledger':False})
        if columns in ('qtr', 'thirteen'):
            res['value'].update({'periods':all_periods})
#         else:
#             if go:
#                 res['value'].update({'periods':periods})
#             else:
#                 res['value'].update({'periods':[]})
        return res

    def onchange_analytic_ledger(self,cr,uid,ids,company_id,analytic_ledger,context=None):
        if context is None:
            context = {}
        context = dict(context)
        context.update({'company_id' : company_id})
        res = {'value':{}}
        cur_id = self.pool.get('res.company').browse(cr,uid,company_id,context=context).currency_id.id
        res['value'].update({'currency_id':cur_id})
        return res

    def onchange_company_id(self,cr,uid,ids,company_id,context=None):
        if context is None:
            context = {}
        context = dict(context)
        context.update({'company_id' : company_id})
        res = {'value':{}}
        if not company_id:
            return res

        cur_id = self.pool.get('res.company').browse(cr,uid,company_id,context=context).currency_id.id
        fy_id = self.pool.get('account.fiscalyear').find(cr, uid,context=context)
        res['value'].update({'fiscalyear':fy_id})
        res['value'].update({'currency_id':cur_id})
        res['value'].update({'account_list':[]})
        res['value'].update({'periods':[]})
        res['value'].update({'afr_id':None})
        return res

    def onchange_afr_id(self,cr,uid,ids,afr_id,context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if not afr_id: return res
        afr_brw = self.pool.get('afr').browse(cr,uid,afr_id,context=context)
        period_date = []
        period_from = ''
        period_to = ''

        for period in afr_brw.period_ids:
            period_date.append(period.date_start)
            period_date.append(period.date_stop)
        period_date.sort()

        for period in afr_brw.period_ids:
            if period_date[0] == period.date_start:
                period_from = period.id
            if period_date[-1] == period.date_stop:
                period_to = period.id
        res['value'].update({'currency_id':afr_brw.currency_id and afr_brw.currency_id.id or afr_brw.company_id.currency_id.id})
        res['value'].update({'inf_type':afr_brw.inf_type or 'BS'})
        res['value'].update({'columns':afr_brw.columns or 'five'})
        res['value'].update({'display_account':afr_brw.display_account or 'bal_mov'})
        res['value'].update({'display_account_level':afr_brw.display_account_level or 0})
        res['value'].update({'fiscalyear':afr_brw.fiscalyear_id and afr_brw.fiscalyear_id.id})
        res['value'].update({'account_list':[acc.id for acc in afr_brw.account_ids]})
#         res['value'].update({'periods':[p.id for p in afr_brw.period_ids]})
        res['value'].update({'org_periods_from':period_from})
        res['value'].update({'org_periods_to':period_to})
        res['value'].update({'analytic_ledger':afr_brw.analytic_ledger or False})
        res['value'].update({'tot_check':afr_brw.tot_check or False})
        res['value'].update({'lab_str':afr_brw.lab_str})
#        res['value'].update({'periodic_columns':afr_brw.columns or 'five'})
        return res

    def _get_defaults(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
           company_id = user.company_id.id
        else:
           company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        data['form']['context'] = context
        return data['form']

    def _check_state(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        if data['form']['filter'] == 'bydate':
           self._check_date(cr, uid, data, context)
        return data['form']

    def _check_date(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        if data['form']['date_from'] > data['form']['date_to']:
            raise osv.except_osv(_('Error !'),('La fecha final debe ser mayor a la inicial'))
        sql = """SELECT f.id, f.date_start, f.date_stop
            FROM account_fiscalyear f
            WHERE '%s' = f.id """%(data['form']['fiscalyear'][0])
        cr.execute(sql)
        res = cr.dictfetchall()
        if res:
            if (data['form']['date_to'] > res[0]['date_stop'] or data['form']['date_from'] < res[0]['date_start']):
                raise osv.except_osv(_('UserError'),'Las fechas deben estar entre %s y %s' % (res[0]['date_start'], res[0]['date_stop']))
            else:
                return 'report'
        else:
            raise osv.except_osv(_('UserError'),'No existe periodo fiscal')

    def _compr0_check_date(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        if data['form']['compr0_date_from'] > data['form']['compr0_date_to']:
            raise osv.except_osv(_('Error !'),('La fecha final debe ser mayor a la inicial'))
        sql = """SELECT f.id, f.date_start, f.date_stop
            FROM account_fiscalyear f
            WHERE '%s' = f.id """%(data['form']['compr0_fiscalyear_id'][0])
        cr.execute(sql)
        res = cr.dictfetchall()

        if res:
            if (data['form']['compr0_date_to'] > res[0]['date_stop'] or data['form']['compr0_date_from'] < res[0]['date_start']):
                raise osv.except_osv(_('UserError'),'Las fechas deben estar entre %s y %s' % (res[0]['date_start'], res[0]['date_stop']))
            else:
                return 'report'
        else:
            raise osv.except_osv(_('UserError'),'No existe periodo fiscal')

    def _compr1_check_date(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        if data['form']['compr1_date_from'] > data['form']['compr1_date_to']:
            raise osv.except_osv(_('Error !'),('La fecha final debe ser mayor a la inicial'))
        sql = """SELECT f.id, f.date_start, f.date_stop
            FROM account_fiscalyear f
            WHERE '%s' = f.id """%(data['form']['compr1_fiscalyear_id'][0])
        cr.execute(sql)
        res = cr.dictfetchall()

        if res:
            if (data['form']['compr1_date_to'] > res[0]['date_stop'] or data['form']['compr1_date_from'] < res[0]['date_start']):
                raise osv.except_osv(_('UserError'),'Las fechas deben estar entre %s y %s' % (res[0]['date_start'], res[0]['date_stop']))
            else:
                return 'report'
        else:
            raise osv.except_osv(_('UserError'),'No existe periodo fiscal')

    def onchange_org_periods_from(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod' and period:
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_start
            res['value'].update({'date_from':periods})
            return res

    def onchange_org_periods_to(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod' and period:
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_stop
            res['value'].update({'date_to':periods})
            return res

    def onchange_compr0_periods_from(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_start
            res['value'].update({'compr0_date_from':periods})
            return res

    def onchange_compr0_periods_to(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_stop
            res['value'].update({'compr0_date_to':periods})
            return res

    def onchange_compr1_periods_from(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_start
            res['value'].update({'compr1_date_from':periods})
            return res

    def onchange_compr1_periods_to(self, cr, uid, ids, filter,period, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if filter == 'byperiod':
            p_obj = self.pool.get("account.period")
            periods = p_obj.browse(cr, uid, period, context=context).date_stop
            res['value'].update({'compr1_date_to':periods})
        return res

    def onchange_date_from(self, cr, uid, ids, date_from, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_from:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_from ), ('date_stop','>=', date_from)], context=context)
            if periods:
                periods_from = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'org_periods_from':periods_from.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def onchange_date_to(self, cr, uid, ids, date_to, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_to:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_to ), ('date_stop','>=', date_to)], context=context)
            if periods:
                periods_to = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'org_periods_to':periods_to.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def onchange_compr0_date_from(self, cr, uid, ids, date_from, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_from:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_from ), ('date_stop','>=', date_from)], context=context)
            if periods:
                periods_from = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'compr0_periods_from':periods_from.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def onchange_compr0_date_to(self, cr, uid, ids, date_to, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_to:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_to ), ('date_stop','>=', date_to)], context=context)
            if periods:
                periods_to = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'compr0_periods_to':periods_to.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def onchange_compr1_date_from(self, cr, uid, ids, date_from, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_from:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_from ), ('date_stop','>=', date_from)], context=context)
            if periods:
                periods_from = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'compr1_periods_from':periods_from.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def onchange_compr1_date_to(self, cr, uid, ids, date_to, fiscalyear, context=None):
        if context is None:
            context = {}
        res = {'value':{}}
        if date_to:
            p_obj = self.pool.get("account.period")
            periods = p_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear),('date_start','<=' ,date_to ), ('date_stop','>=', date_to)], context=context)
            if periods:
                periods_to = p_obj.browse(cr, uid, periods[0], context=context)
                res['value'].update({'compr1_periods_to':periods_to.id})
                return res
            else:
                raise osv.except_osv(_('Warning'),'there is not fiscal year for defined date ')

    def period_span(self, cr, uid, ids, fy_id, context=None):
        if context is None:
            context = {}
        ap_obj = self.pool.get('account.period')
        fy_id = fy_id and type(fy_id) in (list,tuple) and fy_id[0] or fy_id
        if not ids:
            #~ No hay periodos
            return ap_obj.search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False)],order='date_start asc')
        ap_brws = ap_obj.browse(cr, uid, ids, context=context)
        date_start = min([period.date_start for period in ap_brws])
        date_stop = max([period.date_stop for period in ap_brws])
        return ap_obj.search(cr, uid, [('fiscalyear_id','=',fy_id),('special','=',False),('date_start','>=',date_start),('date_stop','<=',date_stop)],order='date_start asc')

    def find_periods(self, cr, uid, ids, period_from, period_to, context=None):
        per_obj = self.pool.get('account.period')
        date_from = per_obj.browse(cr, uid, period_from[0],context = context).date_start
        date_to = per_obj.browse(cr, uid, period_to[0],context = context).date_stop
        return per_obj.search(cr, uid, [('fiscalyear_id','=',ids[0]),('date_start','>=',date_from),('date_stop','<=',date_to)],order='date_start asc')

    def periodic_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids[0])
        ap_obj = self.pool.get('account.period')
        if data['form']['filter'] == 'byperiod':
            data['form']['date_from'] = ''
            data['form']['date_to'] = ''
            data['form']['periods'] = self.find_periods(cr, uid, data['form']['fiscalyear'],data['form']['org_periods_from'], data['form']['org_periods_to'])
        elif data['form']['filter'] == 'bydate':
            self._check_date(cr, uid, data)
            data['form']['periods'] = []
        elif data['form']['filter'] == 'none':
            data['form']['date_from'] = ''
            data['form']['date_to'] = ''
            data['form']['periods'] = []
        elif data['form']['filter'] == False:
            raise osv.except_osv(_('Error !'),_('Select filter in Filters.'))
        else:
            self._check_date(cr, uid, data)
            data['form']['periods'] = self.find_periods(cr, uid, data['form']['fiscalyear'],data['form']['org_periods_from'], data['form']['org_periods_to'])
            period_by_date = str(ap_obj.search(cr, uid, [('fiscalyear_id','=',data['form']['fiscalyear'][0]),('date_start','>=',data['form']['date_from']),('date_stop','<=',data['form']['date_to'])],))
            lis2 = str(data['form']['periods']).replace("[","(").replace("]",")")
            sqlmm = """select min(p.date_start) as inicio, max(p.date_stop) as fin
            from account_period p 
            where p.id in %s""" % lis2
            cr.execute(sqlmm)
            minmax = cr.dictfetchall()
            if minmax:
                if (data['form']['date_to'] < minmax[0]['inicio']) or (data['form']['date_from'] > minmax[0]['fin']):
                    raise osv.except_osv(_('Error !'),_('La interseccion entre el periodo y fecha es vacio'))
        data['form']['compr0_periods'] =[]
        if data['form']['compr0_fiscalyear_id']:
            if data['form']['compr0_filter'] == 'byperiod':
                data['form']['compr0_periods'] = self.find_periods(cr, uid, data['form']['compr0_fiscalyear_id'],data['form']['compr0_periods_from'], data['form']['compr0_periods_to'])
#                data['form']['compr0_periods'] = ap_obj.search(cr, uid, [('fiscalyear_id','=',data['form']['compr0_fiscalyear_id'][0]),('date_start','>=',data['form']['compr0_date_from']),('date_stop','<=',data['form']['compr0_date_to'])], )
                data['form']['compr0_date_from'] = ''
                data['form']['compr0_date_to'] = ''
            elif data['form']['compr0_filter'] == "bydate":
                self._compr0_check_date(cr, uid, data)
                data['form']['compr0_periods_from'] = ''
                data['form']['compr0_periods_to'] = ''
            elif data['form']['compr0_filter'] == 'none':
                data['form']['compr0_date_from'] = ''
                data['form']['compr0_date_to'] =''
                data['form']['compr0_periods_from'] = ''
                data['form']['compr0_periods_to'] = ''
            elif data['form']['compr1_filter'] == False:    
                raise osv.except_osv(_('Error !'),_('Select filter in Comparison1.'))
            else:
                self._compr0_check_date(cr, uid, data)
                lis2 = str(ap_obj.search(cr, uid, [('fiscalyear_id','=',data['form']['compr0_fiscalyear_id'][0]),('date_start','>=',data['form']['compr0_date_from']),('date_stop','<=',data['form']['compr0_date_to'])], ))
                sqlmm = """select min(p.date_start) as inicio, max(p.date_stop) as fin 
                from account_period p 
                where p.id in %s"""% str(lis2).replace("[","(").replace("]",")")
                cr.execute(sqlmm)
                minmax = cr.dictfetchall()
                if minmax:
                    if (data['form']['compr0_date_to'] < minmax[0]['inicio']) or (data['form']['compr0_date_from'] > minmax[0]['fin']):
                        raise osv.except_osv(_('Error !'),_('La interseccion entre el periodo y fecha es vacio'))
        data['form']['compr1_periods'] = []
        if data['form']['compr1_fiscalyear_id']:
            if data['form']['compr1_filter'] == 'byperiod':
                data['form']['compr1_periods'] = self.find_periods(cr, uid, data['form']['compr1_fiscalyear_id'],data['form']['compr1_periods_from'], data['form']['compr1_periods_to'])
                data['form']['compr1_date_from'] = ''
                data['form']['compr1_date_to'] = ''
            elif data['form']['compr1_filter'] == "bydate":
                self._compr1_check_date(cr, uid, data)
                data['form']['compr1_periods_from'] = ''
                data['form']['compr1_periods_to'] = ''
            elif data['form']['compr1_filter'] == 'none':
                data['form']['compr1_date_from'] = ''
                data['form']['compr1_date_to'] = ''
                data['form']['compr1_periods_from'] = ''
                data['form']['compr1_periods_to'] = ''
            elif data['form']['compr1_filter'] == False:
                raise osv.except_osv(_('Error !'),_('Select filter in Comparison2.'))
            else:
                self._compr1_check_date(cr, uid, data)
                lis2 = str(ap_obj.search(cr, uid, [('fiscalyear_id','=',data['form']['compr1_fiscalyear_id'][0]),('date_start','>=',data['form']['compr1_date_from']),('date_stop','<=',data['form']['compr1_date_to'])], ))
                sqlmm = """select min(p.date_start) as inicio, max(p.date_stop) as fin 
                from account_period p 
                where p.id in %s"""% str(lis2).replace("[","(").replace("]",")")
                cr.execute(sqlmm)
                minmax = cr.dictfetchall()
                if minmax:
                    if (data['form']['compr1_date_to'] < minmax[0]['inicio']) or (data['form']['compr1_date_from'] > minmax[0]['fin']):
                        raise osv.except_osv(_('Error !'),_('La interseccion entre el periodo y fecha es vacio'))
        if data['form']['periodic_columns'] == 'one':
            name = 'periodic1.1cols'
        if data['form']['periodic_columns'] == 'two':
            name="periodic.2cols"
        if data['form']['compr0_fiscalyear_id'] and data['form']['periodic_columns'] == 'one':
            name = 'periodic2.1cols'
        if data['form']['compr1_fiscalyear_id'] and data['form']['periodic_columns'] == 'one':
            name = 'periodic3.1cols'
        if data['form']['compr0_fiscalyear_id'] and data['form']['periodic_columns'] == 'two':
            name = 'periodic1.2cols'
        if data['form']['compr1_fiscalyear_id'] and data['form']['periodic_columns'] == 'two':
            name = 'periodic2.2cols'
        if data['form']['periodic_columns'] == 'four':
            if data['form']['inf_type'] == 'GL':
                name = 'afr.analytic.ledger'
            else:
                name = 'periodic.4cols'
        if data['form']['periodic_columns'] == 'four' and data['form']['compr0_fiscalyear_id']:
                name = 'periodic2.4cols'
        if data['form']['periodic_columns'] == 'four' and data['form']['compr1_fiscalyear_id']:
                name = 'periodic3.4cols'
        return {'type': 'ir.actions.report.xml', 'report_name': name, 'datas': data}


    def print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids[0])
        account_period_obj = self.pool.get('account.period')
        if data['form']['columns'] == 'one':
            name = 'afr.1cols1.inherit'
        if data['form']['columns'] == 'two':
            name = 'afr.2cols.inherit'
        if data['form']['columns'] == 'four':
            name = 'afr.4cols'
        if data['form']['columns'] == 'five':
            name = 'afr.5cols'
        if data['form']['columns'] == 'qtr':
            name = 'afr.qtrcols'
        if data['form']['columns'] == 'thirteen':
            name = 'afr.13cols'
        return {'type': 'ir.actions.report.xml', 'report_name': name, 'datas': data}
    
    
    def print_report_xls(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        context.update({'inf_type': data['inf_type'], 'form': data})
        return {
          'name': _('Binary'),
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'bs.pl.xls.report',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: