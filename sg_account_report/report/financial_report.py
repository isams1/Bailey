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

import time
import datetime
from openerp.report import report_sxw
from openerp.tools import config
from openerp.tools.translate import _
from openerp.osv import osv
from operator import itemgetter
from openerp.addons.sg_account_report.report.parser import account_balance

class account_balance_inherit(account_balance):
    def __init__(self, cr, uid, name, context):
#        self.total_asset_credit = 0.00
#        self.total_liabilities_credit = 0.00
#        self.total_equity_credit = 0.00
#        self.total_asset_debit = 0.00
#        self.total_liabilities_debit = 0.00
#        self.total_equity_debit = 0.00
        self.total_liabilities_equity = 0.00
#        self.total_assets = 0.00
        
#        self.rev_credit = 0.00
#        self.rev_debit = 0.00
#        self.cogs_credit = 0.00
#        self.cogs_debit = 0.00
        self.gross_profit = 0.00
        self.bal = 0.00
        self.total_balance_sheet_balance = 0.00
            
        self.other_exp_credit = 0.00
        self.other_exp_debit = 0.00
        self.exp_credit = 0.00
        self.exp_debit = 0.00
#        self.taxes_credit = 0.00
#        self.taxes_debit = 0.00
        self.net_profit = 0.00
        self.total_exp = 0.00
        self.other_income_credit = 0.00
        self.other_income_debit = 0.00
        
        self.debit_total = 0.00
        self.credit_total = 0.00
        
        self.comp_debit_total = 0.00
        self.comp_credit_total = 0.00
        
        self.net_income_loss = 0.00
        self.net_income_credit = 0.00
        self.net_income_debit = 0.00
#        self.total_balance_of_bs = 0.00
#        self.net_profit_loss_periodic = 0.00
#        self.total_balance_of_bs_periodic = 0.00
        self.total_liabilities_equity_new = 0.00
        self.liab = 0.00
        self.equ = 0.00
#        self.total_liab_periodic = 0.00
#        self.total_equ_periodic = 0.00
#        self.total_liab_equ_periodic = 0.00
#        self.profit_loss_comp1 = 0.00
#        self.profit_loss_comp0 = 0.00
#        self.total_liab_comp0 = 0.00
#        self.total_liab_comp1 = 0.00
#        self.total_equ_comp0 = 0.00
#        self.total_equ_comp1 = 0.00
#        self.total_liab_equ_comp0 = 0.00
#        self.total_liab_equ_comp1 = 0.00
        
        self.total_liabilities_equity_new_debit = 0.0 
        self.liab_debit = 0.0
        self.equ_debit = 0.0
        
        self.total_liabilities_equity_new_credit = 0.0
        self.liab_credit = 0.0
        self.equ_credit = 0.0
        
        self.net_income_balanceinit = 0.0
        self.net_income_ytd = 0.0
        self.liab_balanceinit = 0.0
        self.liab_ytd = 0.0
        self.equ_balanceinit = 0.0
        self.equ_ytd = 0.0
        self.total_liabilities_equity_new_balanceinit = 0.0
        self.total_liabilities_equity_new_ytd = 0.0
        
        self.net_income_balance = 0.0
        self.liab_balance = 0.0
        self.equ_balance = 0.0
        self.total_liabilities_equity_new_balance = 0.0
        
        self.tot_revenue_mon_dbr1 = 0.0
        self.tot_revenue_mon_dbr2 = 0.0
        self.tot_revenue_mon_dbr3 = 0.0
        self.tot_revenue_mon_dbr4 = 0.0
        self.tot_revenue_mon_dbr5 = 0.0
        self.tot_revenue_mon_dbr6 = 0.0
        self.tot_revenue_mon_dbr7 = 0.0
        self.tot_revenue_mon_dbr8 = 0.0
        self.tot_revenue_mon_dbr9 = 0.0
        self.tot_revenue_mon_dbr10 = 0.0
        self.tot_revenue_mon_dbr11 = 0.0
        self.tot_revenue_mon_dbr12 = 0.0
        self.tot_revenue_mon_dbr13 = 0.0
        
        self.tot_other_revenue_mon_dbr1 = 0.0
        self.tot_other_revenue_mon_dbr2 = 0.0
        self.tot_other_revenue_mon_dbr3 = 0.0
        self.tot_other_revenue_mon_dbr4 = 0.0
        self.tot_other_revenue_mon_dbr5 = 0.0
        self.tot_other_revenue_mon_dbr6 = 0.0
        self.tot_other_revenue_mon_dbr7 = 0.0
        self.tot_other_revenue_mon_dbr8 = 0.0
        self.tot_other_revenue_mon_dbr9 = 0.0
        self.tot_other_revenue_mon_dbr10 = 0.0
        self.tot_other_revenue_mon_dbr11 = 0.0
        self.tot_other_revenue_mon_dbr12 = 0.0
        self.tot_other_revenue_mon_dbr13 = 0.0
        
        self.tgcs_mon_dbr1 = 0.0
        self.tgcs_mon_dbr2 = 0.0
        self.tgcs_mon_dbr3 = 0.0
        self.tgcs_mon_dbr4 = 0.0
        self.tgcs_mon_dbr5 = 0.0
        self.tgcs_mon_dbr6 = 0.0
        self.tgcs_mon_dbr7 = 0.0
        self.tgcs_mon_dbr8 = 0.0
        self.tgcs_mon_dbr9 = 0.0
        self.tgcs_mon_dbr10 = 0.0
        self.tgcs_mon_dbr11 = 0.0
        self.tgcs_mon_dbr12 = 0.0
        self.tgcs_mon_dbr13 = 0.0
        
        self.exp_new_1 = 0.0
        self.exp_new_2 = 0.0
        self.exp_new_3 = 0.0
        self.exp_new_4 = 0.0
        self.exp_new_5 = 0.0
        self.exp_new_6 = 0.0
        self.exp_new_7 = 0.0
        self.exp_new_8 = 0.0
        self.exp_new_9 = 0.0
        self.exp_new_10 = 0.0
        self.exp_new_11 = 0.0
        self.exp_new_12 = 0.0
        self.exp_new_13 = 0.0
        
        self.exp_new_other_1 = 0.0
        self.exp_new_other_2 = 0.0
        self.exp_new_other_3 = 0.0
        self.exp_new_other_4 = 0.0
        self.exp_new_other_5 = 0.0
        self.exp_new_other_6 = 0.0
        self.exp_new_other_7 = 0.0
        self.exp_new_other_8 = 0.0
        self.exp_new_other_9 = 0.0
        self.exp_new_other_10 = 0.0
        self.exp_new_other_11 = 0.0
        self.exp_new_other_12 = 0.0
        self.exp_new_other_13 = 0.0
        
        self.new_bal1 = 0.0
        self.new_bal2 = 0.0
        self.new_bal3 = 0.0
        self.new_bal4 = 0.0
        self.new_bal5 = 0.0
        self.new_bal6 = 0.0
        self.new_bal7 = 0.0
        self.new_bal8 = 0.0
        self.new_bal9 = 0.0
        self.new_bal10 = 0.0
        self.new_bal11 = 0.0
        self.new_bal12 = 0.0
        self.new_bal13 = 0.0
        
        self.bal1 = 0.0
        self.bal2 = 0.0
        self.bal3 = 0.0
        self.bal4 = 0.0
        self.bal5 = 0.0
        self.bal6 = 0.0
        self.bal7 = 0.0
        self.bal8 = 0.0
        self.bal9 = 0.0
        self.bal10 = 0.0
        self.bal11 = 0.0
        self.bal12 = 0.0
        self.bal13 = 0.0
        
        self.liab_bal1 = 0.0
        self.liab_bal2 = 0.0
        self.liab_bal3 = 0.0
        self.liab_bal4 = 0.0
        self.liab_bal5 = 0.0
        self.liab_bal6 = 0.0
        self.liab_bal7 = 0.0
        self.liab_bal8 = 0.0
        self.liab_bal9 = 0.0
        self.liab_bal10 = 0.0
        self.liab_bal11 = 0.0
        self.liab_bal12 = 0.0
        self.liab_bal13 = 0.0
        self.equ_bal1 = 0.0
        self.equ_bal2 = 0.0
        self.equ_bal3 = 0.0
        self.equ_bal4 = 0.0
        self.equ_bal5 = 0.0
        self.equ_bal6 = 0.0
        self.equ_bal7 = 0.0
        self.equ_bal8 = 0.0
        self.equ_bal9 = 0.0
        self.equ_bal10 = 0.0
        self.equ_bal11 = 0.0
        self.equ_bal12 = 0.0
        self.equ_bal13 = 0.0
        self.total_liabilities_equity_new_bal1 = 0.0
        self.total_liabilities_equity_new_bal2 = 0.0
        self.total_liabilities_equity_new_bal3 = 0.0
        self.total_liabilities_equity_new_bal4 = 0.0
        self.total_liabilities_equity_new_bal5 = 0.0
        self.total_liabilities_equity_new_bal6 = 0.0
        self.total_liabilities_equity_new_bal7 = 0.0
        self.total_liabilities_equity_new_bal8 = 0.0
        self.total_liabilities_equity_new_bal9 = 0.0
        self.total_liabilities_equity_new_bal10 = 0.0
        self.total_liabilities_equity_new_bal11 = 0.0
        self.total_liabilities_equity_new_bal12 = 0.0
        self.total_liabilities_equity_new_bal13 = 0.0
        
        self.ce1 = 0.0
        self.ce2 = 0.0
        self.ce3 = 0.0
        self.ce4 = 0.0
        self.ce5 = 0.0
        self.ce6 = 0.0
        self.ce7 = 0.0
        self.ce8 = 0.0
        self.ce9 = 0.0
        self.ce10 = 0.0
        self.ce11 = 0.0
        self.ce12 = 0.0
        self.ce13 = 0.0
    
        self.ca1 = 0.0
        self.ca2 = 0.0
        self.ca3 = 0.0
        self.ca4 = 0.0
        self.ca5 = 0.0
        self.ca6 = 0.0
        self.ca7 = 0.0
        self.ca8 = 0.0
        self.ca9 = 0.0
        self.ca10 = 0.0
        self.ca11 = 0.0
        self.ca12 = 0.0
        self.ca13 = 0.0
    
        self.ppe1 = 0.0
        self.ppe2 = 0.0
        self.ppe3 = 0.0
        self.ppe4 = 0.0
        self.ppe5 = 0.0
        self.ppe6 = 0.0
        self.ppe7 = 0.0
        self.ppe8 = 0.0
        self.ppe9 = 0.0
        self.ppe10 = 0.0
        self.ppe11 = 0.0
        self.ppe12 = 0.0
        self.ppe13 = 0.0
    
        self.nca1 = 0.0
        self.nca2 = 0.0
        self.nca3 = 0.0
        self.nca4 = 0.0
        self.nca5 = 0.0
        self.nca6 = 0.0
        self.nca7 = 0.0
        self.nca8 = 0.0
        self.nca9 = 0.0
        self.nca10 = 0.0
        self.nca11 = 0.0
        self.nca12 = 0.0
        self.nca13 = 0.0
    
        self.tr1 = 0.0
        self.tr2 = 0.0
        self.tr3 = 0.0
        self.tr4 = 0.0
        self.tr5 = 0.0
        self.tr6 = 0.0
        self.tr7 = 0.0
        self.tr8 = 0.0
        self.tr9 = 0.0
        self.tr10 = 0.0
        self.tr11 = 0.0
        self.tr12 = 0.0
        self.tr13 = 0.0
    
        self.pr1 = 0.0
        self.pr2 = 0.0
        self.pr3 = 0.0
        self.pr4 = 0.0
        self.pr5 = 0.0
        self.pr6 = 0.0
        self.pr7 = 0.0
        self.pr8 = 0.0
        self.pr9 = 0.0
        self.pr10 = 0.0
        self.pr11 = 0.0
        self.pr12 = 0.0
        self.pr13 = 0.0
    
        self.ass1 = 0.0
        self.ass2 = 0.0
        self.ass3 = 0.0
        self.ass4 = 0.0
        self.ass5 = 0.0
        self.ass6 = 0.0
        self.ass7 = 0.0
        self.ass8 = 0.0
        self.ass9 = 0.0
        self.ass10 = 0.0
        self.ass11 = 0.0
        self.ass12 = 0.0
        self.ass13 = 0.0
        
        self.cl1 = 0.0
        self.cl2 = 0.0
        self.cl3 = 0.0
        self.cl4 = 0.0
        self.cl5 = 0.0
        self.cl6 = 0.0
        self.cl7 = 0.0
        self.cl8 = 0.0
        self.cl9 = 0.0
        self.cl10 = 0.0
        self.cl11 = 0.0
        self.cl12 = 0.0
        self.cl13 = 0.0
        
        self.ncl1 = 0.0
        self.ncl2 = 0.0
        self.ncl3 = 0.0
        self.ncl4 = 0.0
        self.ncl5 = 0.0
        self.ncl6 = 0.0
        self.ncl7 = 0.0
        self.ncl8 = 0.0
        self.ncl9 = 0.0
        self.ncl10 = 0.0
        self.ncl11 = 0.0
        self.ncl12 = 0.0
        self.ncl13 = 0.0
        
        self.top1 = 0.0
        self.top2 = 0.0
        self.top3 = 0.0
        self.top4 = 0.0
        self.top5 = 0.0
        self.top6 = 0.0
        self.top7 = 0.0
        self.top8 = 0.0
        self.top9 = 0.0
        self.top10 = 0.0
        self.top11 = 0.0
        self.top12 = 0.0
        self.top13 = 0.0
        
        self.eq1 = 0.0
        self.eq2 = 0.0
        self.eq3 = 0.0
        self.eq4 = 0.0
        self.eq5 = 0.0
        self.eq6 = 0.0
        self.eq7 = 0.0
        self.eq8 = 0.0
        self.eq9 = 0.0
        self.eq10 = 0.0
        self.eq11 = 0.0
        self.eq12 = 0.0
        self.eq13 = 0.0
        
        self.stp1 = 0.0
        self.stp2 = 0.0
        self.stp3 = 0.0
        self.stp4 = 0.0
        self.stp5 = 0.0
        self.stp6 = 0.0
        self.stp7 = 0.0
        self.stp8 = 0.0
        self.stp9 = 0.0
        self.stp10 = 0.0
        self.stp11 = 0.0
        self.stp12 = 0.0
        self.stp13 = 0.0
        
#        self.context = context
        
        super(account_balance_inherit, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_debit' : self.get_debit,
            'get_total_debit' : self.get_total_debit,
            'get_credit' : self.get_credit,
            'get_total_credit' : self.get_total_credit,
            'get_comp_debit' : self.get_comp_debit,
            'get_total_comp_debit' : self.get_total_comp_debit,
            'get_comp_credit' : self.get_comp_credit,
            'get_total_comp_credit' : self.get_total_comp_credit
        })
        
    # Calculate the Debit and Credit amount of each line items of the Trail Balance for YTD reports.
        
    def get_debit(self, debit, level, type, name):
        if type in ['other', 'liquidity', 'receivable', 'payable']: 
            self.debit_total += debit
        return debit
    
    def get_total_debit(self):
        return self.debit_total
    
    def get_credit(self, credit, level, type, name):
        if type in ['other', 'liquidity', 'receivable', 'payable']: 
            self.credit_total += credit
        return credit
    
    def get_total_credit(self):
        return self.credit_total
            
    def lines(self, form, level=0):
        """
        Returns all the data needed for the report lines
        (account info plus debit/credit/balance in the selected period
        and the full year)
        """
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        wiz_rep = self.pool.get('wizard.report')
        afr_obj = self.pool.get('afr')
        self.show_earnings = False
        ids = []
        acc_ids = []
        bal = []
        bal_list = []
        dict = {}
#        if 'earning_account' in form and not isinstance(form['earning_account'], int):
#            form['earning_account'] = form['earning_account'][0]
        def _get_children_and_consol(cr, uid, ids, level, context={}, change_sign=False):
            aa_obj = self.pool.get('account.account')
            ids2=[]
            for aa_brw in aa_obj.browse(cr, uid, ids, context):
                if aa_brw.child_id and aa_brw.level < level and aa_brw.type !='consolidation':
                    if not change_sign:
                        ids2.append([aa_brw.id, True, False, aa_brw])
                    ids2 += _get_children_and_consol(cr, uid, [x.id for x in aa_brw.child_id], level, context, change_sign=change_sign)
                    if change_sign:
                        ids2.append(aa_brw.id) 
                    else:
                        ids2.append([aa_brw.id, False, True, aa_brw])
                else:
                    if change_sign:
                        ids2.append(aa_brw.id)
                    else:
                        ids2.append([aa_brw.id, True, True, aa_brw])
            return ids2

        #############################################################################
        # CONTEXT FOR ENDIND BALANCE                                                #
        #############################################################################

        def _ctx_end(ctx):
            ctx_end = ctx
            ctx_end['filter'] = form.get('filter', 'all')
            ctx_end['fiscalyear'] = fiscalyear.id
            #~ ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',False)])
            
            if ctx_end['filter'] not in ['bydate', 'none']:
                special = self.special_period(form['periods'])
            else:
                special = False
            
            if form['filter'] in ['byperiod', 'all']:
                if special:
                    ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('id', 'in', form['periods'] or ctx_end.get('periods', False))])
                else:
                    ctx_end['periods'] = period_obj.search(self.cr, self.uid, [('id','in',form['periods'] or ctx_end.get('periods',False))])
            if form['filter'] in ['bydate', 'all', 'none']:
                ctx_end['date_from'] = form['date_from']
                ctx_end['date_to'] = form['date_to']
            return ctx_end.copy()
        
        def missing_period(ctx_init):
            
            ctx_init['fiscalyear'] = fiscalyear_obj.search(self.cr, self.uid, [('date_stop', '<', fiscalyear.date_start)], order='date_stop') and \
                                fiscalyear_obj.search(self.cr, self.uid, [('date_stop', '<', fiscalyear.date_start)], order='date_stop')[-1] or []
            ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', ctx_init['fiscalyear']), ('date_stop', '<', fiscalyear.date_start)])
            return ctx_init
        #############################################################################
        # CONTEXT FOR INITIAL BALANCE                                               #
        #############################################################################
        
        def _ctx_init(ctx):
            ctx_init = self.context.copy()
            ctx_init['filter'] = form.get('filter', 'all')
            ctx_init['fiscalyear'] = fiscalyear.id

            if form['filter'] in ['byperiod', 'all']:
                ctx_init['periods'] = form['periods']
                if not ctx_init['periods']:
                    ctx_init = missing_period(ctx_init.copy())
                date_start = min([period.date_start for period in period_obj.browse(self.cr, self.uid, ctx_init['periods'])])
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id), ('date_stop', '<=', date_start)])
            elif form['filter'] in ['bydate']:
                ctx_init['date_from'] = fiscalyear.date_start
                ctx_init['date_to'] = form['date_from']
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id), ('date_stop', '<=', ctx_init['date_to'])])
            elif form['filter'] == 'none':
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id), ('special', '=', True)])
#                date_start = min([period.date_start for period in period_obj.browse(self.cr, self.uid, ctx_init['periods'])])
#                print "date_startdate_start",date_start
                ctx_init['periods'] = period_obj.search(self.cr, self.uid, [('fiscalyear_id', '=', fiscalyear.id), ('date_start', '<=', time.strftime('%Y-%m-%d'))])
            return ctx_init.copy()

        def z(n):
            return abs(n) < 0.005 and 0.0 or n
                

        self.from_currency_id = self.get_company_currency(form['company_id'] and type(form['company_id']) in (list, tuple) and form['company_id'][0] or form['company_id'])
        if not form['currency_id']:
            self.to_currency_id = self.from_currency_id
        else:
            self.to_currency_id = form['currency_id'] and type(form['currency_id']) in (list, tuple) and form['currency_id'][0] or form['currency_id']
        selected_accounts = []
        account_ids = []
        if form.has_key('account_list') and form['account_list']:
            selected_accounts = form['account_list']
            account_ids = form['account_list']
#            del form['account_list']
        
        credit_account_ids = self.get_company_accounts(form['company_id'] and type(form['company_id']) in (list, tuple) and form['company_id'][0] or form['company_id'], 'credit')
        
        debit_account_ids = self.get_company_accounts(form['company_id'] and type(form['company_id']) in (list, tuple) and form['company_id'][0] or form['company_id'], 'debit')

        if form.get('fiscalyear'):
            if type(form.get('fiscalyear')) in (list, tuple):
                fiscalyear = form['fiscalyear'] and form['fiscalyear'][0]
            elif type(form.get('fiscalyear')) in (int,):
                fiscalyear = form['fiscalyear']
        fiscalyear = fiscalyear_obj.browse(self.cr, self.uid, fiscalyear)

        ################################################################
        # Get the accounts                                             #
        ################################################################
        
        account_ids = _get_children_and_consol(self.cr, self.uid, account_ids, form['display_account_level'] and form['display_account_level'] or 100, self.context)
        
        credit_account_ids = _get_children_and_consol(self.cr, self.uid, credit_account_ids, 100, self.context, change_sign=True)
        
        debit_account_ids = _get_children_and_consol(self.cr, self.uid, debit_account_ids, 100, self.context, change_sign=True)
        
        credit_account_ids = list(set(credit_account_ids) - set(debit_account_ids))

        #
        # Generate the report lines (checking each account)
        #
        
        tot_check = False
        
        if form['columns'] == 'qtr':
            period_ids = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id)],order='date_start asc')
#            period_ids = [1,2,3,4,5,6,7,8,9,10,11,12,13]
            a=0
            l=[]
            p=[]
            for x in period_ids:
                a+=1
                if a<3:
                        l.append(x+1)
                else:
                        l.append(x+1)
                        p.append(l)
                        l=[]
                        a=0
            
            #~ period_ids = p

        elif form['columns'] == 'thirteen':
#            period_ids = period_obj.search(self.cr, self.uid, [('fiscalyear_id','=',fiscalyear.id)],order='date_start asc')
            period_ids = [2,3,4,5,6,7,8,9,10,11,12,13]

#        if form['columns'] == 'qtr':
#            tot_bal1 = 0.0
#            tot_bal2 = 0.0
#            tot_bal3 = 0.0
#            tot_bal4 = 0.0
#            tot_bal5 = 0.0
#
#        elif form['columns'] == 'thirteen':
#            tot_bal1 = 0.0
#            tot_bal2 = 0.0
#            tot_bal3 = 0.0
#            tot_bal4 = 0.0
#            tot_bal5 = 0.0
#            tot_bal6 = 0.0
#            tot_bal7 = 0.0
#            tot_bal8 = 0.0
#            tot_bal9 = 0.0
#            tot_bal10 = 0.0
#            tot_bal11 = 0.0
#            tot_bal12 = 0.0
#            tot_bal13 = 0.0
#        
#        else:
        ctx_init = _ctx_init(self.context.copy())
        ctx_end = _ctx_end(self.context.copy())
#    
#            tot_bin = 0.0
#            tot_deb = 0.0
#            tot_crd = 0.0
#            tot_ytd = 0.0
#            tot_eje = 0.0
        
        move_obj = self.pool.get('account.move.line')
        res = {}
        result_acc = []
        tot = {}   
        ############################For getting the net balance for earning account
        net_balance = 0.0   
        temp_earning = {}  
        net_bal_temp = {}
        earning_data = {}
        ################################net calculation ends
        for aa_id in account_ids:
            id = aa_id[0]
            #
            # Check if we need to include this level
            #
            if not form['display_account_level'] or aa_id[3].level <= form['display_account_level']:
                res = {
                'id'        : id, 
                'type'      : aa_id[3].type, 
                'code'      : aa_id[3].code, 
                'name'      : (aa_id[2] and not aa_id[1]) and 'Total %s'%(aa_id[3].name) or aa_id[3].name, 
                'parent_id' : aa_id[3].parent_id and aa_id[3].parent_id.id, 
                'level'     : aa_id[3].level, 
                'label'     : aa_id[1], 
                'total'     : aa_id[2], 
                'change_sign' : credit_account_ids and (id  in credit_account_ids and -1 or 1) or 1,
                'month'     : 0.0
                }
                
                if form['columns'] == 'qtr':
                    pn = 1
#                    if [13] not in p: 
#                        p.append([13]
                    for p_id in p:
                        form['periods'] = p_id
                        
                        ctx_init = _ctx_init(self.context.copy())
                        aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                        
                        ctx_end = _ctx_end(self.context.copy())
                        aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                        move_ids = move_obj.search(self.cr, self.uid, [('period_id', 'in', p_id), ('account_id', '=', aa_brw_end.id)])
                        if form['inf_type'] == 'IS':
                            d, c, b = map(z, [aa_brw_end.debit, aa_brw_end.credit, aa_brw_end.balance])
                            if move_ids:
                                res.update({
                                    'dbr%s'%pn: self.exchange(d), 
                                    'cdr%s'%pn: self.exchange(c), 
                                    'bal%s'%pn: self.exchange(b), 
                                })
                                if p_id == [3,2,4]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [5,6,7]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [8,9,10]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [11,12,13]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                            else:
                                res.update({
                                    'dbr%s'%pn: 0.0, 
                                    'cdr%s'%pn: 0.0, 
                                    'bal%s'%pn: 0.0, 
                                })
                        else:
                            b, d, c = map(z, [aa_brw_init.balance, aa_brw_end.debit, aa_brw_end.credit])
#                            b = z(i+d-c)
                            if move_ids:
                                res.update({
                                    'dbr%s'%pn: self.exchange(d), 
                                    'cdr%s'%pn: self.exchange(c), 
                                    'bal%s'%pn: self.exchange(b), 
                                })
                                if p_id == [3,2,4]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [5,6,7]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [8,9,10]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                                if p_id == [11,12,13]:
                                    self.new_bal1 += res.get('bal1')
                                    self.new_bal2 += res.get('bal2')
                                    self.new_bal3 += res.get('bal3')
                                    self.new_bal4 += res.get('bal4')
#                                    self.new_bal5 += res.get('bal5')
                            else:
                                res.update({
                                    'dbr%s'%pn: 0.0, 
                                    'cdr%s'%pn: 0.0, 
                                    'bal%s'%pn: 0.0, 
                                })
                        pn +=1
                    form['periods'] = period_ids
                    
                    ctx_init = _ctx_init(self.context.copy())
                    aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                    
                    ctx_end = _ctx_end(self.context.copy())
                    aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                    
                    if form['inf_type'] == 'IS':
                        d, c, b = map(z, [aa_brw_end.debit, aa_brw_end.credit, aa_brw_init.balance])
                        
#                        tot_revenue_dbr1 = tot_revenue_dbr2 = tot_revenue_dbr3 = tot_revenue_dbr4 = tot_revenue_dbr5 = 0.00
#                        tgcs_dbr1 = tgcs_dbr2 = tgcs_dbr3 = tgcs_dbr4 = tgcs_dbr5 = 0.00
                        res.update({
                            'balance': self.exchange(d-c), 
                        })
                        res.update({
                            'dbr5': self.exchange(d), 
                            'cdr5': self.exchange(c), 
                            'bal5': self.exchange(b), 
                        })
                        
                        if res.get('name').lower() == 'total revenue':
#                            self.tot_revenue = b + float(res.get('balance'))
                            self.tot_revenue_mon_dbr1 = self.new_bal1
                            self.tot_revenue_mon_dbr2 = self.new_bal2
                            self.tot_revenue_mon_dbr3 = self.new_bal3
                            self.tot_revenue_mon_dbr4 = self.new_bal4
                            self.tot_revenue_mon_dbr5 = self.new_bal5
                        
                        if res.get('name').lower() == 'total other revenue':
#                            self.tot_revenue = b + float(res.get('balance'))
                            self.tot_other_revenue_mon_dbr1 = self.new_bal1
                            self.tot_other_revenue_mon_dbr2 = self.new_bal2
                            self.tot_other_revenue_mon_dbr3 = self.new_bal3
                            self.tot_other_revenue_mon_dbr4 = self.new_bal4
                            self.tot_other_revenue_mon_dbr5 = self.new_bal5
                        
                        if res.get('name').lower() == 'total income':
                            res.update({
                                'bal1' : self.tot_revenue_mon_dbr1 + self.tot_other_revenue_mon_dbr1,
                                'bal2' : self.tot_revenue_mon_dbr2 + self.tot_other_revenue_mon_dbr2,
                                'bal3' : self.tot_revenue_mon_dbr3 + self.tot_other_revenue_mon_dbr3,
                                'bal4' : self.tot_revenue_mon_dbr4 + self.tot_other_revenue_mon_dbr4,
#                                'bal5' : self.tot_revenue_mon_dbr5 + self.tot_other_revenue_mon_dbr5,
                            })
                        
                        if res.get('name').lower() == 'total cost of goods sold':
#                            self.tot_cogs = res.get('balance')
                            self.tgcs_mon_dbr1 = self.new_bal1
                            self.tgcs_mon_dbr2 = self.new_bal2
                            self.tgcs_mon_dbr3 = self.new_bal3
                            self.tgcs_mon_dbr4 = self.new_bal4
                            self.tgcs_mon_dbr5 = self.new_bal5
                            
                        if res.get('name').lower() == 'total expenses':
#                            self.tot_cogs = res.get('balance')
                            self.exp_new_1 = self.new_bal1
                            self.exp_new_2 = self.new_bal2
                            self.exp_new_3 = self.new_bal3
                            self.exp_new_4 = self.new_bal4
                            self.exp_new_5 = self.new_bal5
                            
                        if res.get('name').lower() == 'total other expenses':
#                            self.tot_cogs = res.get('balance')
                            self.exp_new_other_1 = self.new_bal1
                            self.exp_new_other_2 = self.new_bal2
                            self.exp_new_other_3 = self.new_bal3
                            self.exp_new_other_4 = self.new_bal4
                            self.exp_new_other_5 = self.new_bal5
                            
                        if res.get('name').lower() == 'total indirect expenses':
#                            self.tot_cogs = res.get('balance')
                            res.update({
                                'bal1' : self.exp_new_1 + self.exp_new_other_1,
                                'bal2' : self.exp_new_1 + self.exp_new_other_1,
                                'bal3' : self.exp_new_3 + self.exp_new_other_3,
                                'bal4' : self.exp_new_4 + self.exp_new_other_4,
#                                'bal5' : self.exp_new_5 + self.exp_new_other_5,
#                                'bal13' : self.new_bal13,
                            })
                        
                        
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             res.update({
                                'bal1' : self.new_bal1,
                                'bal2' : self.new_bal2,
                                'bal3' : self.new_bal3,
                                'bal4' : self.new_bal4,
#                                'bal5' : self.new_bal5,
#                                'bal13' : self.new_bal13,
                             })
                             self.bal1 += res.get('bal1')
                             self.bal2 += res.get('bal2')
                             self.bal3 += res.get('bal3')
                             self.bal4 += res.get('bal4')
                             self.bal5 += res.get('bal5')
                             
                             self.new_bal1 = 0.0
                             self.new_bal2 = 0.0
                             self.new_bal3 = 0.0
                             self.new_bal4 = 0.0
                             self.new_bal5 = 0.0
                        
                        
#                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
#                             self.bal1 += res.get('bal1')
#                             self.bal2 += res.get('bal2')
#                             self.bal3 += res.get('bal3')
#                             self.bal4 += res.get('bal4')
#                             self.bal5 += res.get('bal5')
                    else:
                        b, d, c = map(z, [aa_brw_init.balance, aa_brw_end.debit, aa_brw_end.credit])
#                        b = z(i+d-c)
                        res.update({
                            'balance': self.exchange(d-c), 
                        })
                        res.update({
                            'dbr5': self.exchange(d), 
                            'cdr5': self.exchange(c), 
                            'bal5': self.exchange(b), 
                        })
                        
                        #For Asset Amount and Calculation
                        if res.get('name').lower() == 'total cash and cash equivalents':
                            self.ce1 = self.new_bal1
                            self.ce2 = self.new_bal2
                            self.ce3 = self.new_bal3
                            self.ce4 = self.new_bal4
                            self.ce5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.ce1,
                                'bal2' : self.ce2,
                                'bal3' : self.ce3,
                                'bal4' : self.ce4,
#                                'bal5' : self.ce5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total current assets':
                            self.ca1 = self.new_bal1
                            self.ca2 = self.new_bal2
                            self.ca3 = self.new_bal3
                            self.ca4 = self.new_bal4
                            self.ca5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.ca1,
                                'bal2' : self.ca2,
                                'bal3' : self.ca3,
                                'bal4' : self.ca4,
#                                'bal5' : self.ca5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total property, plant and equivalent':
                            self.ppe1 = self.new_bal1
                            self.ppe2 = self.new_bal2
                            self.ppe3 = self.new_bal3
                            self.ppe4 = self.new_bal4
                            self.ppe5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.ppe1,
                                'bal2' : self.ppe2,
                                'bal3' : self.ppe3,
                                'bal4' : self.ppe4,
#                                'bal5' : self.ppe5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total non-current assets':
                            self.nca1 = self.new_bal1
                            self.nca2 = self.new_bal2
                            self.nca3 = self.new_bal3
                            self.nca4 = self.new_bal4
                            self.nca5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.nca1,
                                'bal2' : self.nca2,
                                'bal3' : self.nca3,
                                'bal4' : self.nca4,
#                                'bal5' : self.nca5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total trade and other receivable':
                            self.tr1 = self.new_bal1
                            self.tr2 = self.new_bal2
                            self.tr3 = self.new_bal3
                            self.tr4 = self.new_bal4
                            self.tr5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.tr1,
                                'bal2' : self.tr2,
                                'bal3' : self.tr3,
                                'bal4' : self.tr4,
#                                'bal5' : self.tr5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total purchase tax receivable':
                            self.pr1 = self.new_bal1
                            self.pr2 = self.new_bal2
                            self.pr3 = self.new_bal3
                            self.pr4 = self.new_bal4
                            self.pr5 = self.new_bal5
                            
                            res.update({
                                'bal1' : self.pr1,
                                'bal2' : self.pr2,
                                'bal3' : self.pr3,
                                'bal4' : self.pr4,
#                                'bal5' : self.pr5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total assets':
                            self.ass1 = self.ce1 + self.ca1 + self.ppe1 + self.nca1 + self.tr1 + self.pr1
                            self.ass2 = self.ce2 + self.ca2 + self.ppe2 + self.nca2 + self.tr2 + self.pr2
                            self.ass3 = self.ce3 + self.ca3 + self.ppe3 + self.nca3 + self.tr3 + self.pr3
                            self.ass4 = self.ce4 + self.ca4 + self.ppe4 + self.nca4 + self.tr4 + self.pr4
                            self.ass5 = self.ce5 + self.ca5 + self.ppe5 + self.nca5 + self.tr5 + self.pr5
                            
                            res.update({
                                'bal1' : self.ass1,
                                'bal2' : self.ass2,
                                'bal3' : self.ass3,
                                'bal4' : self.ass4,
#                                'bal5' : self.ass5,
#                                'bal13' : self.new_bal13,
                             })
                            
                        #For Liabilities Amount and Calculation
                        
                        if res.get('name').lower() == 'total current liabilities':
                            self.cl1 = self.new_bal1
                            self.cl2 = self.new_bal2
                            self.cl3 = self.new_bal3
                            self.cl4 = self.new_bal4
#                            self.cl5 = self.new_bal5
#                            self.cl13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.cl1,
                                'bal2' : self.cl2,
                                'bal3' : self.cl3,
                                'bal4' : self.cl4,
#                                'bal5' : self.cl5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            
                        if res.get('name').lower() == 'total non-current liabilities':
                            self.ncl1 = self.new_bal1
                            self.ncl2 = self.new_bal2
                            self.ncl3 = self.new_bal3
                            self.ncl4 = self.new_bal4
#                            self.ncl5 = self.new_bal5
#                            self.ncl13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.ncl1,
                                'bal2' : self.ncl2,
                                'bal3' : self.ncl3,
                                'bal4' : self.ncl4,
#                                'bal5' : self.ncl5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            
                        if res.get('name').lower() == 'total trade and other payables':
                            self.top1 = self.new_bal1
                            self.top2 = self.new_bal2
                            self.top3 = self.new_bal3
                            self.top4 = self.new_bal4
#                            self.top5 = self.new_bal5
#                            self.top13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.top1,
                                'bal2' : self.top2,
                                'bal3' : self.top3,
                                'bal4' : self.top4,
#                                'bal5' : self.top5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            
                        if res.get('name').lower() == 'total equity':
                            self.eq1 = self.new_bal1
                            self.eq2 = self.new_bal2
                            self.eq3 = self.new_bal3
                            self.eq4 = self.new_bal4
                            self.eq5 = res.get('bal5')
#                            self.eq13 = res.get('bal13')
                            
                            res.update({
                                'bal1' : self.eq1,
                                'bal2' : self.eq2,
                                'bal3' : self.eq3,
                                'bal4' : self.eq4,
#                                'bal5' : self.eq5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            
                        if res.get('name').lower() == 'total sale tax payables':
                            self.stp1 = self.new_bal1
                            self.stp2 = self.new_bal2
                            self.stp3 = self.new_bal3
                            self.stp4 = self.new_bal4
#                            self.stp5 = self.new_bal5
#                            self.stp13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.stp1,
                                'bal2' : self.stp2,
                                'bal3' : self.stp3,
                                'bal4' : self.stp4,
#                                'bal5' : self.stp5,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                        
                        if res.get('name').lower() == 'total liabilities':
                            self.liab_bal1 = self.cl1 + self.ncl1 + self.top1 + self.stp1
                            self.liab_bal2 = self.cl2 + self.ncl2 + self.top2 + self.stp2
                            self.liab_bal3 = self.cl3 + self.ncl3 + self.top3 + self.stp3
                            self.liab_bal4 = self.cl4 + self.ncl4 + self.top4 + self.stp4
                            self.liab_bal5 = res.get('bal5')
#                            self.liab_bal13 = res.get('bal13')
                            
                            res.update({
                                'bal1' : self.liab_bal1,
                                'bal2' : self.liab_bal2,
                                'bal3' : self.liab_bal3,
                                'bal4' : self.liab_bal4,
#                                'bal5' : self.liab_bal5,
#                                'bal13' : self.new_bal13,
                             })
                            
                        self.total_liabilities_equity_new_bal1 = self.liab_bal1 + self.eq1
                        self.total_liabilities_equity_new_bal2 = self.liab_bal2 + self.eq2
                        self.total_liabilities_equity_new_bal3 = self.liab_bal3 + self.eq3
                        self.total_liabilities_equity_new_bal4 = self.liab_bal4 + self.eq4
                        self.total_liabilities_equity_new_bal5 = self.liab_bal5 + self.eq5
                        
#                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Liabilities':
#                            self.liab_bal1 = res.get('bal1')
#                            self.liab_bal2 = res.get('bal2')
#                            self.liab_bal3 = res.get('bal3')
#                            self.liab_bal4 = res.get('bal4')
#                            self.liab_bal5 = res.get('bal5')
#                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Equity':
#                            self.equ_bal1 = res.get('bal1')
#                            self.equ_bal2 = res.get('bal2')
#                            self.equ_bal3 = res.get('bal3')
#                            self.equ_bal4 = res.get('bal4')
#                            self.equ_bal5 = res.get('bal5')
#                        self.total_liabilities_equity_new_bal1 = self.liab_bal1 + self.equ_bal1
#                        self.total_liabilities_equity_new_bal2 = self.liab_bal2 + self.equ_bal2
#                        self.total_liabilities_equity_new_bal3 = self.liab_bal3 + self.equ_bal3
#                        self.total_liabilities_equity_new_bal4 = self.liab_bal4 + self.equ_bal4
#                        self.total_liabilities_equity_new_bal5 = self.liab_bal5 + self.equ_bal5
                
                if form['columns'] == 'thirteen':
                    pn = 1
#                    m = 1
                    for p_id in period_ids:
                        form['periods'] = [p_id]
                        
                        ctx_init = _ctx_init(self.context.copy())
                        aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                        
                        ctx_end = _ctx_end(self.context.copy())
                        aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                        move_ids = move_obj.search(self.cr, self.uid, [('period_id', '=', p_id), ('account_id', '=', aa_brw_end.id)])
                        if form['inf_type'] == 'IS':
                            d, c, b = map(z, [aa_brw_end.debit, aa_brw_end.credit, aa_brw_end.balance])
                            if move_ids:
                                res.update({
                                    'dbr%s'%pn: self.exchange(d), 
                                    'cdr%s'%pn: self.exchange(c), 
                                    'bal%s'%pn: self.exchange(b), 
    #                                'month' : m
                                })
                                if p_id == 2:
                                    self.new_bal1 += res.get('bal1')
                                if p_id == 3:
                                    self.new_bal2 += res.get('bal2')
                                if p_id == 4:
                                    self.new_bal3 += res.get('bal3')
                                if p_id == 5:
                                    self.new_bal4 += res.get('bal4')
                                if p_id == 6:
                                    self.new_bal5 += res.get('bal5')
                                if p_id == 7:
                                    self.new_bal6 += res.get('bal6')
                                if p_id == 8:
                                    self.new_bal7 += res.get('bal7')
                                if p_id == 9:
                                    self.new_bal8 += res.get('bal8')
                                if p_id == 10:
                                    self.new_bal9 += res.get('bal9')
                                if p_id == 11:
                                    self.new_bal10 += res.get('bal10')
                                if p_id == 12:
                                    self.new_bal11 += res.get('bal11')
                                if p_id == 13:
                                    self.new_bal12 += res.get('bal12')
#                                if p_id == 13:
#                                    self.new_bal13 += res.get('bal13')
                            else:
                                res.update({
                                    'dbr%s'%pn: 0.0, 
                                    'cdr%s'%pn: 0.0, 
                                    'bal%s'%pn: 0.0, 
#                                    'month' : m
                                })
                        else:
                            b, d, c = map(z, [aa_brw_init.balance, aa_brw_end.debit, aa_brw_end.credit])
#                            b = z(i+d-c)
                            if move_ids:
                                res.update({
                                    'dbr%s'%pn: self.exchange(d), 
                                    'cdr%s'%pn: self.exchange(c), 
                                    'bal%s'%pn: self.exchange(b), 
                                })
                                if p_id == 2:
                                    self.new_bal1 += res.get('bal1')
                                if p_id == 3:
                                    self.new_bal2 += res.get('bal2')
                                if p_id == 4:
                                    self.new_bal3 += res.get('bal3')
                                if p_id == 5:
                                    self.new_bal4 += res.get('bal4')
                                if p_id == 6:
                                    self.new_bal5 += res.get('bal5')
                                if p_id == 7:
                                    self.new_bal6 += res.get('bal6')
                                if p_id == 8:
                                    self.new_bal7 += res.get('bal7')
                                if p_id == 9:
                                    self.new_bal8 += res.get('bal8')
                                if p_id == 10:
                                    self.new_bal9 += res.get('bal9')
                                if p_id == 11:
                                    self.new_bal10 += res.get('bal10')
                                if p_id == 12:
                                    self.new_bal11 += res.get('bal11')
                                if p_id == 13:
                                    self.new_bal12 += res.get('bal12')
#                                if p_id == 13:
#                                    self.new_bal13 += res.get('bal13')
                            else:
                                res.update({
                                    'dbr%s'%pn: 0.0, 
                                    'cdr%s'%pn: 0.0, 
                                    'bal%s'%pn: 0.0, 
                                })
                        pn +=1
#                        m += 1
                    form['periods'] = period_ids
                    ctx_init = _ctx_init(self.context.copy())
                    aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                    
                    ctx_end = _ctx_end(self.context.copy())
                    aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                    if form['inf_type'] == 'IS':
                        d, c, b = map(z, [aa_brw_end.debit, aa_brw_end.credit, aa_brw_init.balance])
                        
#                        tot_revenue_dbr1 = tot_revenue_dbr2 = tot_revenue_dbr3 = tot_revenue_dbr4 = tot_revenue_dbr5 = 0.00
#                        tgcs_dbr1 = tgcs_dbr2 = tgcs_dbr3 = tgcs_dbr4 = tgcs_dbr5 = 0.00
                        res.update({
                            'balance': self.exchange(d-c), 
                        })
                        res.update({
                            'dbr13': self.exchange(d), 
                            'cdr13': self.exchange(c), 
                            'bal13': self.exchange(b),
                        })
                        
                        if res.get('name').lower() == 'total revenue':
#                            self.tot_revenue = b + float(res.get('balance'))
                            self.tot_revenue_mon_dbr1 = self.new_bal1
                            self.tot_revenue_mon_dbr2 = self.new_bal2
                            self.tot_revenue_mon_dbr3 = self.new_bal3
                            self.tot_revenue_mon_dbr4 = self.new_bal4
                            self.tot_revenue_mon_dbr5 = self.new_bal5
                            self.tot_revenue_mon_dbr6 = self.new_bal6
                            self.tot_revenue_mon_dbr7 = self.new_bal7
                            self.tot_revenue_mon_dbr8 = self.new_bal8
                            self.tot_revenue_mon_dbr9 = self.new_bal9
                            self.tot_revenue_mon_dbr10 = self.new_bal10
                            self.tot_revenue_mon_dbr11 = self.new_bal11
                            self.tot_revenue_mon_dbr12 = self.new_bal12
                            self.tot_revenue_mon_dbr13 = self.new_bal13
                        
                        if res.get('name').lower() == 'total other revenue':
#                            self.tot_revenue = b + float(res.get('balance'))
                            self.tot_other_revenue_mon_dbr1 = self.new_bal1
                            self.tot_other_revenue_mon_dbr2 = self.new_bal2
                            self.tot_other_revenue_mon_dbr3 = self.new_bal3
                            self.tot_other_revenue_mon_dbr4 = self.new_bal4
                            self.tot_other_revenue_mon_dbr5 = self.new_bal5
                            self.tot_other_revenue_mon_dbr6 = self.new_bal6
                            self.tot_other_revenue_mon_dbr7 = self.new_bal7
                            self.tot_other_revenue_mon_dbr8 = self.new_bal8
                            self.tot_other_revenue_mon_dbr9 = self.new_bal9
                            self.tot_other_revenue_mon_dbr10 = self.new_bal10
                            self.tot_other_revenue_mon_dbr11 = self.new_bal11
                            self.tot_other_revenue_mon_dbr12 = self.new_bal12
                            self.tot_other_revenue_mon_dbr13 = self.new_bal13
                        
                        if res.get('name').lower() == 'total income':
                            res.update({
                                'bal1' : self.tot_revenue_mon_dbr1 + self.tot_other_revenue_mon_dbr1,
                                'bal2' : self.tot_revenue_mon_dbr2 + self.tot_other_revenue_mon_dbr2,
                                'bal3' : self.tot_revenue_mon_dbr3 + self.tot_other_revenue_mon_dbr3,
                                'bal4' : self.tot_revenue_mon_dbr4 + self.tot_other_revenue_mon_dbr4,
                                'bal5' : self.tot_revenue_mon_dbr5 + self.tot_other_revenue_mon_dbr5,
                                'bal6' : self.tot_revenue_mon_dbr6 + self.tot_other_revenue_mon_dbr6,
                                'bal7' : self.tot_revenue_mon_dbr7 + self.tot_other_revenue_mon_dbr7,
                                'bal8' : self.tot_revenue_mon_dbr8 + self.tot_other_revenue_mon_dbr8,
                                'bal9' : self.tot_revenue_mon_dbr9 + self.tot_other_revenue_mon_dbr9,
                                'bal10' : self.tot_revenue_mon_dbr10 + self.tot_other_revenue_mon_dbr10,
                                'bal11' : self.tot_revenue_mon_dbr11 + self.tot_other_revenue_mon_dbr11,
                                'bal12' : self.tot_revenue_mon_dbr12 + self.tot_other_revenue_mon_dbr12,
#                                'bal13' : self.new_bal13,
                            })
                        
                        if res.get('name').lower() == 'total cost of goods sold':
#                            self.tot_cogs = res.get('balance')
                            self.tgcs_mon_dbr1 = self.new_bal1
                            self.tgcs_mon_dbr2 = self.new_bal2
                            self.tgcs_mon_dbr3 = self.new_bal3
                            self.tgcs_mon_dbr4 = self.new_bal4
                            self.tgcs_mon_dbr5 = self.new_bal5
                            self.tgcs_mon_dbr6 = self.new_bal6
                            self.tgcs_mon_dbr7 = self.new_bal7
                            self.tgcs_mon_dbr8 = self.new_bal8
                            self.tgcs_mon_dbr9 = self.new_bal9
                            self.tgcs_mon_dbr10 = self.new_bal10
                            self.tgcs_mon_dbr11 = self.new_bal11
                            self.tgcs_mon_dbr12 = self.new_bal12
                            self.tgcs_mon_dbr13 = self.new_bal13
                            
                        if res.get('name').lower() == 'total expenses':
#                            self.tot_cogs = res.get('balance')
                            self.exp_new_1 = self.new_bal1
                            self.exp_new_2 = self.new_bal2
                            self.exp_new_3 = self.new_bal3
                            self.exp_new_4 = self.new_bal4
                            self.exp_new_5 = self.new_bal5
                            self.exp_new_6 = self.new_bal6
                            self.exp_new_7 = self.new_bal7
                            self.exp_new_8 = self.new_bal8
                            self.exp_new_9 = self.new_bal9
                            self.exp_new_10 = self.new_bal10
                            self.exp_new_11 = self.new_bal11
                            self.exp_new_12 = self.new_bal12
                            self.exp_new_13 = self.new_bal13
                            
                        if res.get('name').lower() == 'total other expenses':
#                            self.tot_cogs = res.get('balance')
                            self.exp_new_other_1 = self.new_bal1
                            self.exp_new_other_2 = self.new_bal2
                            self.exp_new_other_3 = self.new_bal3
                            self.exp_new_other_4 = self.new_bal4
                            self.exp_new_other_5 = self.new_bal5
                            self.exp_new_other_6 = self.new_bal6
                            self.exp_new_other_7 = self.new_bal7
                            self.exp_new_other_8 = self.new_bal8
                            self.exp_new_other_9 = self.new_bal9
                            self.exp_new_other_10 = self.new_bal10
                            self.exp_new_other_11 = self.new_bal11
                            self.exp_new_other_12 = self.new_bal12
                            self.exp_new_other_13 = self.new_bal13
                            
                        if res.get('name').lower() == 'total indirect expenses':
#                            self.tot_cogs = res.get('balance')
                            res.update({
                                'bal1' : self.exp_new_1 + self.exp_new_other_1,
                                'bal2' : self.exp_new_1 + self.exp_new_other_1,
                                'bal3' : self.exp_new_3 + self.exp_new_other_3,
                                'bal4' : self.exp_new_4 + self.exp_new_other_4,
                                'bal5' : self.exp_new_5 + self.exp_new_other_5,
                                'bal6' : self.exp_new_6 + self.exp_new_other_6,
                                'bal7' : self.exp_new_7 + self.exp_new_other_7,
                                'bal8' : self.exp_new_8 + self.exp_new_other_8,
                                'bal9' : self.exp_new_9 + self.exp_new_other_9,
                                'bal10' : self.exp_new_10 + self.exp_new_other_10,
                                'bal11' : self.exp_new_11 + self.exp_new_other_11,
                                'bal12' : self.exp_new_12 + self.exp_new_other_12,
#                                'bal13' : self.new_bal13,
                            })
                        
                        
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             res.update({
                                'bal1' : self.new_bal1,
                                'bal2' : self.new_bal2,
                                'bal3' : self.new_bal3,
                                'bal4' : self.new_bal4,
                                'bal5' : self.new_bal5,
                                'bal6' : self.new_bal6,
                                'bal7' : self.new_bal7,
                                'bal8' : self.new_bal8,
                                'bal9' : self.new_bal9,
                                'bal10' : self.new_bal10,
                                'bal11' : self.new_bal11,
                                'bal12' : self.new_bal12,
#                                'bal13' : self.new_bal13,
                             })
                             self.bal1 += res.get('bal1')
                             self.bal2 += res.get('bal2')
                             self.bal3 += res.get('bal3')
                             self.bal4 += res.get('bal4')
                             self.bal5 += res.get('bal5')
                             self.bal6 += res.get('bal6')
                             self.bal7 += res.get('bal7')
                             self.bal8 += res.get('bal8')
                             self.bal9 += res.get('bal9')
                             self.bal10 += res.get('bal10')
                             self.bal11 += res.get('bal11')
                             self.bal12 += res.get('bal12')
                             self.bal13 += res.get('bal13')
                             
                             self.new_bal1 = 0.0
                             self.new_bal2 = 0.0
                             self.new_bal3 = 0.0
                             self.new_bal4 = 0.0
                             self.new_bal5 = 0.0
                             self.new_bal6 = 0.0
                             self.new_bal7 = 0.0
                             self.new_bal8 = 0.0
                             self.new_bal9 = 0.0
                             self.new_bal10 = 0.0
                             self.new_bal11 = 0.0
                             self.new_bal12 = 0.0
                             self.new_bal13 = 0.0
                             
                    else:
                        b, d, c = map(z, [aa_brw_init.balance, aa_brw_end.debit, aa_brw_end.credit])
#                        b = z(i+d-c)
                        res.update({
                            'balance': self.exchange(d-c), 
                        })
                        res.update({
                            'dbr13': self.exchange(d), 
                            'cdr13': self.exchange(c), 
                            'bal13': self.exchange(b), 
                        })
                        
                        #For Asset Amount and Calculation
                        if res.get('name').lower() == 'total cash and cash equivalents':
                            self.ce1 = self.new_bal1
                            self.ce2 = self.new_bal2
                            self.ce3 = self.new_bal3
                            self.ce4 = self.new_bal4
                            self.ce5 = self.new_bal5
                            self.ce6 = self.new_bal6
                            self.ce7 = self.new_bal7
                            self.ce8 = self.new_bal8
                            self.ce9 = self.new_bal9
                            self.ce10 = self.new_bal10
                            self.ce11 = self.new_bal11
                            self.ce12 = self.new_bal12
                            self.ce13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.ce1,
                                'bal2' : self.ce2,
                                'bal3' : self.ce3,
                                'bal4' : self.ce4,
                                'bal5' : self.ce5,
                                'bal6' : self.ce6,
                                'bal7' : self.ce7,
                                'bal8' : self.ce8,
                                'bal9' : self.ce9,
                                'bal10' : self.ce10,
                                'bal11' : self.ce11,
                                'bal12' : self.ce12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total current assets':
                            self.ca1 = self.new_bal1
                            self.ca2 = self.new_bal2
                            self.ca3 = self.new_bal3
                            self.ca4 = self.new_bal4
                            self.ca5 = self.new_bal5
                            self.ca6 = self.new_bal6
                            self.ca7 = self.new_bal7
                            self.ca8 = self.new_bal8
                            self.ca9 = self.new_bal9
                            self.ca10 = self.new_bal10
                            self.ca11 = self.new_bal11
                            self.ca12 = self.new_bal12
                            self.ca13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.ca1,
                                'bal2' : self.ca2,
                                'bal3' : self.ca3,
                                'bal4' : self.ca4,
                                'bal5' : self.ca5,
                                'bal6' : self.ca6,
                                'bal7' : self.ca7,
                                'bal8' : self.ca8,
                                'bal9' : self.ca9,
                                'bal10' : self.ca10,
                                'bal11' : self.ca11,
                                'bal12' : self.ca12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total property, plant and equivalent':
                            self.ppe1 = self.new_bal1
                            self.ppe2 = self.new_bal2
                            self.ppe3 = self.new_bal3
                            self.ppe4 = self.new_bal4
                            self.ppe5 = self.new_bal5
                            self.ppe6 = self.new_bal6
                            self.ppe7 = self.new_bal7
                            self.ppe8 = self.new_bal8
                            self.ppe9 = self.new_bal9
                            self.ppe10 = self.new_bal10
                            self.ppe11 = self.new_bal11
                            self.ppe12 = self.new_bal12
                            self.ppe13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.ppe1,
                                'bal2' : self.ppe2,
                                'bal3' : self.ppe3,
                                'bal4' : self.ppe4,
                                'bal5' : self.ppe5,
                                'bal6' : self.ppe6,
                                'bal7' : self.ppe7,
                                'bal8' : self.ppe8,
                                'bal9' : self.ppe9,
                                'bal10' : self.ppe10,
                                'bal11' : self.ppe11,
                                'bal12' : self.ppe12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total non-current assets':
                            self.nca1 = self.new_bal1
                            self.nca2 = self.new_bal2
                            self.nca3 = self.new_bal3
                            self.nca4 = self.new_bal4
                            self.nca5 = self.new_bal5
                            self.nca6 = self.new_bal6
                            self.nca7 = self.new_bal7
                            self.nca8 = self.new_bal8
                            self.nca9 = self.new_bal9
                            self.nca10 = self.new_bal10
                            self.nca11 = self.new_bal11
                            self.nca12 = self.new_bal12
                            self.nca13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.nca1,
                                'bal2' : self.nca2,
                                'bal3' : self.nca3,
                                'bal4' : self.nca4,
                                'bal5' : self.nca5,
                                'bal6' : self.nca6,
                                'bal7' : self.nca7,
                                'bal8' : self.nca8,
                                'bal9' : self.nca9,
                                'bal10' : self.nca10,
                                'bal11' : self.nca11,
                                'bal12' : self.nca12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total trade and other receivable':
                            self.tr1 = self.new_bal1
                            self.tr2 = self.new_bal2
                            self.tr3 = self.new_bal3
                            self.tr4 = self.new_bal4
                            self.tr5 = self.new_bal5
                            self.tr6 = self.new_bal6
                            self.tr7 = self.new_bal7
                            self.tr8 = self.new_bal8
                            self.tr9 = self.new_bal9
                            self.tr10 = self.new_bal10
                            self.tr11 = self.new_bal11
                            self.tr12 = self.new_bal12
                            self.tr13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.tr1,
                                'bal2' : self.tr2,
                                'bal3' : self.tr3,
                                'bal4' : self.tr4,
                                'bal5' : self.tr5,
                                'bal6' : self.tr6,
                                'bal7' : self.tr7,
                                'bal8' : self.tr8,
                                'bal9' : self.tr9,
                                'bal10' : self.tr10,
                                'bal11' : self.tr11,
                                'bal12' : self.tr12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total purchase tax receivable':
                            self.pr1 = self.new_bal1
                            self.pr2 = self.new_bal2
                            self.pr3 = self.new_bal3
                            self.pr4 = self.new_bal4
                            self.pr5 = self.new_bal5
                            self.pr6 = self.new_bal6
                            self.pr7 = self.new_bal7
                            self.pr8 = self.new_bal8
                            self.pr9 = self.new_bal9
                            self.pr10 = self.new_bal10
                            self.pr11 = self.new_bal11
                            self.pr12 = self.new_bal12
                            self.pr13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.pr1,
                                'bal2' : self.pr2,
                                'bal3' : self.pr3,
                                'bal4' : self.pr4,
                                'bal5' : self.pr5,
                                'bal6' : self.pr6,
                                'bal7' : self.pr7,
                                'bal8' : self.pr8,
                                'bal9' : self.pr9,
                                'bal10' : self.pr10,
                                'bal11' : self.pr11,
                                'bal12' : self.pr12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total assets':
                            self.ass1 = self.ce1 + self.ca1 + self.ppe1 + self.nca1 + self.tr1 + self.pr1
                            self.ass2 = self.ce2 + self.ca2 + self.ppe2 + self.nca2 + self.tr2 + self.pr2
                            self.ass3 = self.ce3 + self.ca3 + self.ppe3 + self.nca3 + self.tr3 + self.pr3
                            self.ass4 = self.ce4 + self.ca4 + self.ppe4 + self.nca4 + self.tr4 + self.pr4
                            self.ass5 = self.ce5 + self.ca5 + self.ppe5 + self.nca5 + self.tr5 + self.pr5
                            self.ass6 = self.ce6 + self.ca6 + self.ppe6 + self.nca6 + self.tr6 + self.pr6
                            self.ass7 = self.ce7 + self.ca7 + self.ppe7 + self.nca7 + self.tr7 + self.pr7
                            self.ass8 = self.ce8 + self.ca8 + self.ppe8 + self.nca8 + self.tr8 + self.pr8
                            self.ass9 = self.ce9 + self.ca9 + self.ppe9 + self.nca9 + self.tr9 + self.pr9
                            self.ass10 = self.ce10 + self.ca10 + self.ppe10 + self.nca10 + self.tr10 + self.pr10
                            self.ass11 = self.ce11 + self.ca11 + self.ppe11 + self.nca11 + self.tr11 + self.pr11
                            self.ass12 = self.ce12 + self.ca12 + self.ppe12 + self.nca12 + self.tr12 + self.pr12
                            self.ass13 = self.ce13 + self.ca13 + self.ppe13 + self.nca13 + self.tr13 + self.pr13
                            
                            res.update({
                                'bal1' : self.ass1,
                                'bal2' : self.ass2,
                                'bal3' : self.ass3,
                                'bal4' : self.ass4,
                                'bal5' : self.ass5,
                                'bal6' : self.ass6,
                                'bal7' : self.ass7,
                                'bal8' : self.ass8,
                                'bal9' : self.ass9,
                                'bal10' : self.ass10,
                                'bal11' : self.ass11,
                                'bal12' : self.ass12,
#                                'bal13' : self.new_bal13,
                             })
                            
                        #For Liabilities Amount and Calculation
                        
                        if res.get('name').lower() == 'total current liabilities':
                            self.cl1 = self.new_bal1
                            self.cl2 = self.new_bal2
                            self.cl3 = self.new_bal3
                            self.cl4 = self.new_bal4
                            self.cl5 = self.new_bal5
                            self.cl6 = self.new_bal6
                            self.cl7 = self.new_bal7
                            self.cl8 = self.new_bal8
                            self.cl9 = self.new_bal9
                            self.cl10 = self.new_bal10
                            self.cl11 = self.new_bal11
                            self.cl12 = self.new_bal12
#                            self.cl13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.cl1,
                                'bal2' : self.cl2,
                                'bal3' : self.cl3,
                                'bal4' : self.cl4,
                                'bal5' : self.cl5,
                                'bal6' : self.cl6,
                                'bal7' : self.cl7,
                                'bal8' : self.cl8,
                                'bal9' : self.cl9,
                                'bal10' : self.cl10,
                                'bal11' : self.cl11,
                                'bal12' : self.cl12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                            
                        if res.get('name').lower() == 'total non-current liabilities':
                            self.ncl1 = self.new_bal1
                            self.ncl2 = self.new_bal2
                            self.ncl3 = self.new_bal3
                            self.ncl4 = self.new_bal4
                            self.ncl5 = self.new_bal5
                            self.ncl6 = self.new_bal6
                            self.ncl7 = self.new_bal7
                            self.ncl8 = self.new_bal8
                            self.ncl9 = self.new_bal9
                            self.ncl10 = self.new_bal10
                            self.ncl11 = self.new_bal11
                            self.ncl12 = self.new_bal12
#                            self.ncl13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.ncl1,
                                'bal2' : self.ncl2,
                                'bal3' : self.ncl3,
                                'bal4' : self.ncl4,
                                'bal5' : self.ncl5,
                                'bal6' : self.ncl6,
                                'bal7' : self.ncl7,
                                'bal8' : self.ncl8,
                                'bal9' : self.ncl9,
                                'bal10' : self.ncl10,
                                'bal11' : self.ncl11,
                                'bal12' : self.ncl12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                            
                        if res.get('name').lower() == 'total trade and other payables':
                            self.top1 = self.new_bal1
                            self.top2 = self.new_bal2
                            self.top3 = self.new_bal3
                            self.top4 = self.new_bal4
                            self.top5 = self.new_bal5
                            self.top6 = self.new_bal6
                            self.top7 = self.new_bal7
                            self.top8 = self.new_bal8
                            self.top9 = self.new_bal9
                            self.top10 = self.new_bal10
                            self.top11 = self.new_bal11
                            self.top12 = self.new_bal12
#                            self.top13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.top1,
                                'bal2' : self.top2,
                                'bal3' : self.top3,
                                'bal4' : self.top4,
                                'bal5' : self.top5,
                                'bal6' : self.top6,
                                'bal7' : self.top7,
                                'bal8' : self.top8,
                                'bal9' : self.top9,
                                'bal10' : self.top10,
                                'bal11' : self.top11,
                                'bal12' : self.top12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                            
                        if res.get('name').lower() == 'total equity':
                            self.eq1 = self.new_bal1
                            self.eq2 = self.new_bal2
                            self.eq3 = self.new_bal3
                            self.eq4 = self.new_bal4
                            self.eq5 = self.new_bal5
                            self.eq6 = self.new_bal6
                            self.eq7 = self.new_bal7
                            self.eq8 = self.new_bal8
                            self.eq9 = self.new_bal9
                            self.eq10 = self.new_bal10
                            self.eq11 = self.new_bal11
                            self.eq12 = self.new_bal12
                            self.eq13 = res.get('bal13')
                            
                            res.update({
                                'bal1' : self.eq1,
                                'bal2' : self.eq2,
                                'bal3' : self.eq3,
                                'bal4' : self.eq4,
                                'bal5' : self.eq5,
                                'bal6' : self.eq6,
                                'bal7' : self.eq7,
                                'bal8' : self.eq8,
                                'bal9' : self.eq9,
                                'bal10' : self.eq10,
                                'bal11' : self.eq11,
                                'bal12' : self.eq12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                            
                        if res.get('name').lower() == 'total sale tax payables':
                            self.stp1 = self.new_bal1
                            self.stp2 = self.new_bal2
                            self.stp3 = self.new_bal3
                            self.stp4 = self.new_bal4
                            self.stp5 = self.new_bal5
                            self.stp6 = self.new_bal6
                            self.stp7 = self.new_bal7
                            self.stp8 = self.new_bal8
                            self.stp9 = self.new_bal9
                            self.stp10 = self.new_bal10
                            self.stp11 = self.new_bal11
                            self.stp12 = self.new_bal12
#                            self.stp13 = self.new_bal13
                            
                            res.update({
                                'bal1' : self.stp1,
                                'bal2' : self.stp2,
                                'bal3' : self.stp3,
                                'bal4' : self.stp4,
                                'bal5' : self.stp5,
                                'bal6' : self.stp6,
                                'bal7' : self.stp7,
                                'bal8' : self.stp8,
                                'bal9' : self.stp9,
                                'bal10' : self.stp10,
                                'bal11' : self.stp11,
                                'bal12' : self.stp12,
#                                'bal13' : self.new_bal13,
                             })
                            
                            self.new_bal1 = 0.0
                            self.new_bal2 = 0.0
                            self.new_bal3 = 0.0
                            self.new_bal4 = 0.0
                            self.new_bal5 = 0.0
                            self.new_bal6 = 0.0
                            self.new_bal7 = 0.0
                            self.new_bal8 = 0.0
                            self.new_bal9 = 0.0
                            self.new_bal10 = 0.0
                            self.new_bal11 = 0.0
                            self.new_bal12 = 0.0
                            self.new_bal13 = 0.0
                        
                        if res.get('name').lower() == 'total liabilities':
                            self.liab_bal1 = self.cl1 + self.ncl1 + self.top1 + self.stp1
                            self.liab_bal2 = self.cl2 + self.ncl2 + self.top2 + self.stp2
                            self.liab_bal3 = self.cl3 + self.ncl3 + self.top3 + self.stp3
                            self.liab_bal4 = self.cl4 + self.ncl4 + self.top4 + self.stp4
                            self.liab_bal5 = self.cl5 + self.ncl5 + self.top5 + self.stp5
                            self.liab_bal6 = self.cl6 + self.ncl6 + self.top6 + self.stp6
                            self.liab_bal7 = self.cl7 + self.ncl7 + self.top7 + self.stp7
                            self.liab_bal8 = self.cl8 + self.ncl8 + self.top8 + self.stp8
                            self.liab_bal9 = self.cl9 + self.ncl9 + self.top9 + self.stp9
                            self.liab_bal10 = self.cl10 + self.ncl10 + self.top10 + self.stp10
                            self.liab_bal11 = self.cl11 + self.ncl11 + self.top11 + self.stp11
                            self.liab_bal12 = self.cl12 + self.ncl12 + self.top12 + self.stp12
                            self.liab_bal13 = res.get('bal13')
                            
                            res.update({
                                'bal1' : self.liab_bal1,
                                'bal2' : self.liab_bal2,
                                'bal3' : self.liab_bal3,
                                'bal4' : self.liab_bal4,
                                'bal5' : self.liab_bal5,
                                'bal6' : self.liab_bal6,
                                'bal7' : self.liab_bal7,
                                'bal8' : self.liab_bal8,
                                'bal9' : self.liab_bal9,
                                'bal10' : self.liab_bal10,
                                'bal11' : self.liab_bal11,
                                'bal12' : self.liab_bal12,
#                                'bal13' : self.new_bal13,
                             })
                            
                        self.total_liabilities_equity_new_bal1 = self.liab_bal1 + self.eq1
                        self.total_liabilities_equity_new_bal2 = self.liab_bal2 + self.eq2
                        self.total_liabilities_equity_new_bal3 = self.liab_bal3 + self.eq3
                        self.total_liabilities_equity_new_bal4 = self.liab_bal4 + self.eq4
                        self.total_liabilities_equity_new_bal5 = self.liab_bal5 + self.eq5
                        self.total_liabilities_equity_new_bal6 = self.liab_bal6 + self.eq6
                        self.total_liabilities_equity_new_bal7 = self.liab_bal7 + self.eq7
                        self.total_liabilities_equity_new_bal8 = self.liab_bal8 + self.eq8
                        self.total_liabilities_equity_new_bal9 = self.liab_bal9 + self.eq9
                        self.total_liabilities_equity_new_bal10 = self.liab_bal10 + self.eq10
                        self.total_liabilities_equity_new_bal11 = self.liab_bal11 + self.eq11
                        self.total_liabilities_equity_new_bal12 = self.liab_bal12 + self.eq12
                        self.total_liabilities_equity_new_bal13 = self.liab_bal13 + self.eq13
                
                # Tow, Four and Five columns
                aa_brw_init = account_obj.browse(self.cr, self.uid, id, ctx_init)
                aa_brw_end  = account_obj.browse(self.cr, self.uid, id, ctx_end)
                b, d, c = map(z, [aa_brw_init.balance, aa_brw_end.debit, aa_brw_end.credit])
#                b = z(i+d-c)
                res.update({
                    'balanceinit': self.exchange(b), 
                    'debit': self.exchange(d), 
                    'credit': self.exchange(c), 
                    'ytd': self.exchange(d-c),
                    'balance': self.exchange(b), 
                })
                
                if form['columns'] == 'five':
                    if form['inf_type'] == 'IS':
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             self.net_income_credit += res.get('credit')
                             self.net_income_debit += res.get('debit')
                             self.net_income_balanceinit += res.get('balanceinit')
                             self.net_income_ytd += res.get('ytd')
                             self.net_income_balance += res.get('balance')
                    else:
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Liabilities':
                            self.liab_credit = res.get('credit')
                            self.liab_debit = res.get('debit')
                            self.liab_balanceinit = res.get('balanceinit')
                            self.liab_ytd = res.get('ytd')
                            self.liab_balance = res.get('balance')
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Equity':
                            self.equ_credit = res.get('credit')
                            self.equ_debit = res.get('debit')
                            self.equ_balanceinit = res.get('balanceinit')
                            self.equ_ytd = res.get('ytd')
                            self.equ_balance = res.get('balance')
                        self.total_liabilities_equity_new_credit = self.liab_credit + self.equ_credit
                        self.total_liabilities_equity_new_debit = self.liab_debit + self.equ_debit
                        self.total_liabilities_equity_new_balanceinit = self.liab_balanceinit + self.equ_balanceinit
                        self.total_liabilities_equity_new_ytd = self.liab_ytd + self.equ_ytd
                        self.total_liabilities_equity_new_balance = self.liab_balance + self.equ_balance
                
                if form['columns'] == 'four':
                    if form['inf_type'] == 'IS':
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             self.net_income_credit += res.get('credit')
                             self.net_income_debit += res.get('debit')
                             self.net_income_balanceinit += res.get('balanceinit')
                             self.net_income_ytd += res.get('ytd')
                    else:
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Liabilities':
                            self.liab_credit = res.get('credit')
                            self.liab_debit = res.get('debit')
                            self.liab_balanceinit = res.get('balanceinit')
                            self.liab_ytd = res.get('ytd')
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Equity':
                            self.equ_credit = res.get('credit')
                            self.equ_debit = res.get('debit')
                            self.equ_balanceinit = res.get('balanceinit')
                            self.equ_ytd = res.get('ytd')
                        self.total_liabilities_equity_new_credit = self.liab_credit + self.equ_credit
                        self.total_liabilities_equity_new_debit = self.liab_debit + self.equ_debit
                        self.total_liabilities_equity_new_balanceinit = self.liab_balanceinit + self.equ_balanceinit
                        self.total_liabilities_equity_new_ytd = self.liab_ytd + self.equ_ytd
                
                if form['columns'] == 'two':
                    if form['inf_type'] == 'IS':
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             self.net_income_credit += res.get('credit')
                             self.net_income_debit += res.get('debit')
                    else:
                        if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 3:
                             self.net_income_credit += res.get('credit')
                             self.net_income_debit += res.get('debit')
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Liabilities':
                            self.liab_credit = res.get('credit')
                            self.liab_debit = res.get('debit')
                        if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Equity':
                            self.equ_credit = res.get('credit')
                            self.equ_debit = res.get('debit')
                        self.total_liabilities_equity_new_credit = self.liab_credit + self.equ_credit
                        self.total_liabilities_equity_new_debit = self.liab_debit + self.equ_debit
                ctx_month = ctx_init.copy()
                if form.get('periods'):
#                    ctx_month.update({'periods': [form.get('period_id')[0]]})
                    ctx_month.update({'periods': form.get('periods')})
                    aa_brw_init_month = account_obj.browse(self.cr, self.uid, id, ctx_month)
                    aa_brw_end_month  = account_obj.browse(self.cr, self.uid, id, ctx_month)
                    im, dm, cm = map(z, [aa_brw_init_month.balance, aa_brw_end_month.debit, aa_brw_end_month.credit])
                    res.update({
                        'month': abs(self.exchange(dm-cm)) or 0.0, 
                    })
                
                # End balance
                if form['inf_type'] == 'IS' and form['columns'] == 'one':
                     #PROFIT & LOSS
                     res.update({
                         'balance': abs(self.exchange(d-c)), 
                     })
                     
                     # Checking the Values of the Single Column Income Statement YTD reports
                     report_data = wiz_rep.browse(self.cr, self.uid, self.context.get('active_id'))
                     for ytd_acc_data in report_data.account_list:
                         if ytd_acc_data.type == 'view':
                             parent_id = ytd_acc_data.parent_id.id
                     parent_acc_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',False)])
                     child_acc_ids = account_obj.search(self.cr, self.uid, ['|',('parent_id','in',parent_acc_ids),('level','=',1)])
                     for acc_data in account_obj.browse(self.cr, self.uid, child_acc_ids):
                         if parent_id == acc_data.id:
                             acc_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',acc_data.id)])
                             if res.get('total') == True and res.get('type') == 'view':
                                 self.bal = self.bal + res.get('balance')
                             bal = []
                             for res_acc in result_acc:
                                 if res_acc.get('name')=='Total Net Ordinary Income':
                                     balance_res = res_acc.get('balance')
                                     bal.append(balance_res)
                             if len(bal) > 0 :
                                 self.gross_profit = bal[0]
 #                                self.gross_profit = self.bal
                             
                             for acc in account_obj.browse(self.cr, self.uid, acc_ids):
                                 if acc.name == 'Cost Of Goods Sold' or acc.name == 'Cost of Sales' and acc.user_type.name == 'Income View' or acc.user_type.name == 'Income':
                                     if res.get('name').lower() == 'total cost of sales':
                                         result_acc.append({'id': False, 'name': ''})
                                 
                                 if acc.user_type.name == 'Expense' or acc.user_type.name == 'Expense View':
                                     self.total_exp = (self.exp_credit + self.exp_debit) + (self.other_exp_credit + self.other_exp_debit)
                                 self.net_profit = self.gross_profit - ((self.other_income_credit + self.other_income_debit) + self.total_exp)
                     if res.get('total')== True and res.get('type') == 'view' and res.get('level') == 2:
                         self.net_income_loss += res.get('ytd')

                if form['inf_type'] == 'BS' and form['columns'] == 'one':
                    #END BALANCE SHEET
                    res.update({
                        'balance': self.exchange(b), 
                    })
                    # Checking the Values of the Single Column Balance Sheet YTD reports
                    report_data = wiz_rep.browse(self.cr, self.uid, self.context.get('active_id'))
                    for ytd_acc_data in report_data.account_list:
                        if ytd_acc_data.type == 'view':
                            parent_id = ytd_acc_data.parent_id.id
                        else:
                            parent_id = ytd_acc_data.parent_id.id
                    parent_acc_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',False)])
                    child_acc_ids = account_obj.search(self.cr, self.uid, ['|',('parent_id','in',parent_acc_ids),('level','=',1)])
                    for acc_data in account_obj.browse(self.cr, self.uid, child_acc_ids):
                        if parent_id == acc_data.id:
                            acc_ids = account_obj.search(self.cr, self.uid, [('parent_id','=',acc_data.id)])
                            if res.get('total') == True and res.get('type') == 'view' and res.get('parent_id') == acc_data.id:
                                self.total_balance_sheet_balance = self.total_balance_sheet_balance + res.get('balance')
                            self.total_liabilities_equity = self.total_balance_sheet_balance
                    
                    if res.get('name') == 'Total Balance Sheet':
                        res.update({'name' : '', 'balanceinit' : False, 'ytd' : False, 'balance' : False})
                    if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Liabilities':
                        self.liab = res.get('balance')
                    if res.get('total') == True and res.get('type') == 'view' and res.get('name') == 'Total Equity':
                        self.equ = res.get('balance')
                    self.total_liabilities_equity_new = self.liab + self.equ
                    
                # Check whether we must include this line in the report or not
                #
                to_include = False
                
                if form['display_account'] == 'mov' and aa_id[3].parent_id:
                    # Include accounts with movements
                    if abs(d) >= 0.005 or abs(c) >= 0.005:
                        to_include = True
                elif form['display_account'] == 'bal' and aa_id[3].parent_id:
                    # Include accounts with balance
                    if abs(b) >= 0.005:
                        to_include = True
                elif form['display_account'] == 'bal_mov' and aa_id[3].parent_id:
                    # Include accounts with balance or movements
                    if abs(b) >= 0.005 or abs(d) >= 0.005 or abs(c) >= 0.005:
                        to_include = True
                else:
                    # Include all accounts
                    to_include = True
                        
                if to_include:
                    #result_acc.append(res)
                    if not ((res['id'] in [x['id'] for x in result_acc]) and (res['name'] in [x['name'] for x in result_acc])):
                        result_acc.append(res)
                    #
                    # Check whether we must sumarize this line in the report or not
                    #
        # Added the Net Income(Loss) and Total Liabilities & Equity lines in Balance Sheet and Income Statement reports of the YTD.
        afr_list = []
        if form['inf_type'] == 'BS':
            afr_ids = afr_obj.search(self.cr, self.uid, [('name', '=', 'Income Statement')])

            if afr_ids:
                afr_data = afr_obj.browse(self.cr, self.uid, afr_ids[0]).account_ids
                for afr_id in afr_data:
                    afr_list.append(afr_id.id)
            form['account_list'] = afr_list
            form_copy = form.copy()
            form_copy['inf_type'] = 'IS'
            self.lines(form_copy, 0)
            
            # Added Net Income(Loss) line in Balance Sheet Report
            if form['columns'] =='one':
                total_profit_loss = self.net_income_loss
                self.total_profit_loss = {
                    'balance' : total_profit_loss, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : total_profit_loss, 
                    'month': 0.0,
                }
                result_acc.append(self.total_profit_loss)
            
            if form['columns'] =='two':
                total_profit_credit = self.net_income_credit
                total_profit_debit = self.net_income_debit
                self.total_profit_loss = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_profit_credit, 
                    'debit' : total_profit_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                }
                result_acc.append(self.total_profit_loss)
            
            if form['columns'] =='four':
                total_profit_credit = self.net_income_credit
                total_profit_debit = self.net_income_debit
                total_profit_balanceinit = self.net_income_balanceinit
                total_profit_ytd = self.net_income_ytd
                self.total_profit_loss = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_profit_credit, 
                    'debit' : total_profit_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : total_profit_balanceinit, 
                    'ytd' : total_profit_ytd, 
                    'month': 0.0,
                }
                result_acc.append(self.total_profit_loss)
                
            if form['columns'] =='five':
                total_profit_credit = self.net_income_credit
                total_profit_debit = self.net_income_debit
                total_profit_balanceinit = self.net_income_balanceinit
                total_profit_ytd = self.net_income_ytd
                total_profit_balance = self.net_income_balance
                self.total_profit_loss = {
                    'balance' : total_profit_balance, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_profit_credit, 
                    'debit' : total_profit_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : total_profit_balanceinit, 
                    'ytd' : total_profit_ytd, 
                    'month': 0.0,
                }
                result_acc.append(self.total_profit_loss)
                
            if form['columns'] =='qtr':
                self.total_profit_loss = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                    'bal1': self.bal1,
                    'bal2': self.bal2,
                    'bal3': self.bal3,
                    'bal4': self.bal4,
                    'bal5': self.bal5,
                }
                result_acc.append(self.total_profit_loss)
                
            if form['columns'] =='thirteen':
                self.total_profit_loss = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Net Income (Loss)', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                    'bal1': self.bal1,
                    'bal2': self.bal2,
                    'bal3': self.bal3,
                    'bal4': self.bal4,
                    'bal5': self.bal5,
                    'bal6': self.bal6,
                    'bal7': self.bal7,
                    'bal8': self.bal8,
                    'bal9': self.bal9,
                    'bal10': self.bal10,
                    'bal11': self.bal11,
                    'bal12': self.bal12,
                    'bal13': self.bal13,
                }
                result_acc.append(self.total_profit_loss)
                
                
            if form['columns'] =='one':
                total_liab_equ = self.total_liabilities_equity_new + self.net_income_loss
                self.total_liab_equ = {
                    'balance' : total_liab_equ, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : total_liab_equ, 
                    'month': 0.0,
                }
                result_acc.append(self.total_liab_equ)
            
            if form['columns'] =='two':
                total_liab_credit = self.total_liabilities_equity_new_credit + self.net_income_credit
                total_liab_debit = self.total_liabilities_equity_new_debit + self.net_income_debit
                self.total_liab_equ = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_liab_credit, 
                    'debit' : total_liab_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                }
                result_acc.append(self.total_liab_equ)
                
            if form['columns'] =='four':
                total_liab_credit = self.total_liabilities_equity_new_credit + self.net_income_credit
                total_liab_debit = self.total_liabilities_equity_new_debit + self.net_income_debit
                total_liab_balanceinit = self.total_liabilities_equity_new_balanceinit + self.net_income_balanceinit
                total_liab_ytd = self.total_liabilities_equity_new_ytd + self.net_income_ytd
                self.total_liab_equ = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_liab_credit, 
                    'debit' : total_liab_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : total_liab_balanceinit, 
                    'ytd' : total_liab_ytd, 
                    'month': 0.0,
                }
                result_acc.append(self.total_liab_equ)
                
            if form['columns'] =='five':
                total_liab_credit = self.total_liabilities_equity_new_credit + self.net_income_credit
                total_liab_debit = self.total_liabilities_equity_new_debit + self.net_income_debit
                total_liab_balanceinit = self.total_liabilities_equity_new_balanceinit + self.net_income_balanceinit
                total_liab_ytd = self.total_liabilities_equity_new_ytd + self.net_income_ytd
                total_liab_balance = self.total_liabilities_equity_new_balance + self.net_income_balance
                self.total_liab_equ = {
                    'balance' : total_liab_balance, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : total_liab_credit, 
                    'debit' : total_liab_debit, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : total_liab_balanceinit, 
                    'ytd' : total_liab_ytd, 
                    'month': 0.0,
                }
                result_acc.append(self.total_liab_equ)
                
            if form['columns'] =='qtr':
                total_liabilities_equitydbr1 = self.total_liabilities_equity_new_bal1 + self.bal1
                total_liabilities_equitydbr2 = self.total_liabilities_equity_new_bal2 + self.bal2
                total_liabilities_equitydbr3 = self.total_liabilities_equity_new_bal3 + self.bal3
                total_liabilities_equitydbr4 = self.total_liabilities_equity_new_bal4 + self.bal4
                total_liabilities_equitydbr5 = self.total_liabilities_equity_new_bal5 + self.bal5
                self.total_liab_equ = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                    'bal1': total_liabilities_equitydbr1,
                    'bal2': total_liabilities_equitydbr2,
                    'bal3': total_liabilities_equitydbr3,
                    'bal4': total_liabilities_equitydbr4,
                    'bal5': total_liabilities_equitydbr5,
                }
                result_acc.append(self.total_liab_equ)
            
            if form['columns'] =='thirteen':
                total_liabilities_equitydbr1 = self.total_liabilities_equity_new_bal1 + self.bal1
                total_liabilities_equitydbr2 = self.total_liabilities_equity_new_bal2 + self.bal2
                total_liabilities_equitydbr3 = self.total_liabilities_equity_new_bal3 + self.bal3
                total_liabilities_equitydbr4 = self.total_liabilities_equity_new_bal4 + self.bal4
                total_liabilities_equitydbr5 = self.total_liabilities_equity_new_bal5 + self.bal5
                total_liabilities_equitydbr6 = self.total_liabilities_equity_new_bal6 + self.bal6
                total_liabilities_equitydbr7 = self.total_liabilities_equity_new_bal7 + self.bal7
                total_liabilities_equitydbr8 = self.total_liabilities_equity_new_bal8 + self.bal8
                total_liabilities_equitydbr9 = self.total_liabilities_equity_new_bal9 + self.bal9
                total_liabilities_equitydbr10 = self.total_liabilities_equity_new_bal10 + self.bal10
                total_liabilities_equitydbr11 = self.total_liabilities_equity_new_bal11 + self.bal11
                total_liabilities_equitydbr12 = self.total_liabilities_equity_new_bal12 + self.bal12
                total_liabilities_equitydbr13 = self.total_liabilities_equity_new_bal13 + self.bal13
                self.total_liab_equ = {
                    'balance' : 0.0, 
                    'id' : False, 
                    'type' : 'view', 
                    'code' : '', 
                    'name' : 'Total Liabilities & Equity', 
                    'parent_id' : False, 
                    'level' : 1, 
                    'credit' : 0.0, 
                    'debit' : 0.0, 
                    'label' : False, 
                    'mayor' : [], 
                    'total' :True, 
                    'change_sign' : 1, 
                    'balanceinit' : 0.0, 
                    'ytd' : 0.0, 
                    'month': 0.0,
                    'bal1': total_liabilities_equitydbr1,
                    'bal2': total_liabilities_equitydbr2,
                    'bal3': total_liabilities_equitydbr3,
                    'bal4': total_liabilities_equitydbr4,
                    'bal5': total_liabilities_equitydbr5,
                    'bal6': total_liabilities_equitydbr6,
                    'bal7': total_liabilities_equitydbr7,
                    'bal8': total_liabilities_equitydbr8,
                    'bal9': total_liabilities_equitydbr9,
                    'bal10': total_liabilities_equitydbr10,
                    'bal11': total_liabilities_equitydbr11,
                    'bal12': total_liabilities_equitydbr12,
                    'bal13': total_liabilities_equitydbr13,
                }
                result_acc.append(self.total_liab_equ)
                
        else:
            # Added Net Income(Loss) line in Income Statement Report
            if not form['afr_id'][1] == 'Balance Sheet':
                if not form['inf_type'] == 'TB':
                    if form['columns'] =='one':
                        total_net_profit = self.net_income_loss
        #                        dbr3 = self.gross_profit_dbr3
                        self.net_profit_dict = {
                            'balance' : total_net_profit, 
                            'id': False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income(Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : 0.0, 
                            'debit' : 0.0, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : 0.0, 
                            'ytd' : total_net_profit, 
                            'month': 0.0,
                        }
                        result_acc.append(self.net_profit_dict)
                    
                    if form['columns'] =='two':
                        total_profit_credit = self.net_income_credit
                        total_profit_debit = self.net_income_debit
                        self.net_profit_dict = {
                            'balance' : 0.0, 
                            'id' : False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income (Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : total_profit_credit, 
                            'debit' : total_profit_debit, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : 0.0, 
                            'ytd' : 0.0, 
                            'month': 0.0,
                        }
                        result_acc.append(self.net_profit_dict)
                        
                    if form['columns'] =='four':
                        total_profit_credit = self.net_income_credit
                        total_profit_debit = self.net_income_debit
                        total_profit_balanceinit = self.net_income_balanceinit
                        total_profit_ytd = self.net_income_ytd
                        self.net_profit_dict = {
                            'balance' : 0.0, 
                            'id' : False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income (Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : total_profit_credit, 
                            'debit' : total_profit_debit, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : total_profit_balanceinit, 
                            'ytd' : total_profit_ytd, 
                            'month': 0.0,
                        }
                        result_acc.append(self.net_profit_dict)
                    if form['columns'] =='five':
                        total_profit_credit = self.net_income_credit
                        total_profit_debit = self.net_income_debit
                        total_profit_balanceinit = self.net_income_balanceinit
                        total_profit_ytd = self.net_income_ytd
                        total_profit_balance = self.net_income_balance
                        self.net_profit_dict = {
                            'balance' : total_profit_balance, 
                            'id' : False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income (Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : total_profit_credit, 
                            'debit' : total_profit_debit, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : total_profit_balanceinit, 
                            'ytd' : total_profit_ytd, 
                            'month': 0.0,
                        }
                        result_acc.append(self.net_profit_dict)
                        
                        
                    if form['columns'] =='qtr':
                        self.net_profit_dict = {
                            'balance' : 0.0, 
                            'id' : False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income (Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : 0.0, 
                            'debit' : 0.0, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : 0.0, 
                            'ytd' : 0.0, 
                            'month': 0.0,
                            'bal1': self.bal1,
                            'bal2': self.bal2,
                            'bal3': self.bal3,
                            'bal4': self.bal4,
                            'bal5': self.bal5,
                        }
                        result_acc.append(self.net_profit_dict)
                    
                    if form['columns'] =='thirteen':
                        self.net_profit_dict = {
                            'balance' : 0.0, 
                            'id' : False, 
                            'type' : 'view', 
                            'code' : '', 
                            'name' : 'Net Income (Loss)', 
                            'parent_id' : False, 
                            'level' : 1, 
                            'credit' : 0.0, 
                            'debit' : 0.0, 
                            'label' : False, 
                            'mayor' : [], 
                            'total' :True, 
                            'change_sign' : 1, 
                            'balanceinit' : 0.0, 
                            'ytd' : 0.0, 
                            'month': 0.0,
                            'bal1': self.bal1,
                            'bal2': self.bal2,
                            'bal3': self.bal3,
                            'bal4': self.bal4,
                            'bal5': self.bal5,
                            'bal6': self.bal6,
                            'bal7': self.bal7,
                            'bal8': self.bal8,
                            'bal9': self.bal9,
                            'bal10': self.bal10,
                            'bal11': self.bal11,
                            'bal12': self.bal12,
                            'bal13': self.bal13,
                        }
                        result_acc.append(self.net_profit_dict)
        return result_acc
    
    # Calculate the amount Debit and Credit of the Trail Blanace of Periodic.  
    
    def get_profit(self, bal):
        return bal
    
    def get_comp_debit(self, comp_debit, level, type, name):
        if type in ['other', 'liquidity', 'receivable', 'payable']: 
            self.comp_debit_total += comp_debit
        return comp_debit
    
    def get_total_comp_debit(self):
        return self.comp_debit_total
    
    def get_comp_credit(self, comp_credit, level, type, name):
        if type in ['other', 'liquidity', 'receivable', 'payable']: 
            self.comp_credit_total += comp_credit
        return comp_credit
    
    def get_total_comp_credit(self):
        return self.comp_credit_total

report_sxw.report_sxw('report.afr.1cols1.inherit', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full.rml', 
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.2cols.inherit', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full_2_cols.rml',
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.4cols', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full_4_cols.rml', 
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.5cols', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full_5_cols.rml', 
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.qtrcols', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full_qtr_cols.rml', 
                       parser=account_balance_inherit, 
                       header=False)

report_sxw.report_sxw('report.afr.13cols', 
                      'wizard.report', 
                      'addons/sg_account_report/report/balance_full_13_cols.rml', 
                       parser=account_balance_inherit, 
                       header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: