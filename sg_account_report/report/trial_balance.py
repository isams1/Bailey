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
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header

class account_balance(report_sxw.rml_parse, common_report_header):
    _inherit = 'report.account.account.balance'

    def __init__(self, cr, uid, name, context=None):
        super(account_balance, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.ytd_sum_debit = 0.00
        self.ytd_sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'get_sum_debit': self.get_sum_debit,
            'get_sum_credit': self.get_sum_credit,
            'get_sum_ytd_debit': self.get_sum_ytd_debit,
            'get_sum_ytd_credit': self.get_sum_ytd_credit,
            'get_period': self.get_period,
        })
        self.context = context

    def get_period(self, form):
        return form.get('period_id')[1]

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_balance, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
            account_rec = [acct for acct in accounts if acct['id']==parent][0]
            currency_obj = self.pool.get('res.currency')
            acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
            currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
            res = {
                'id': account_rec['id'],
                'type': account_rec['type'],
                'code': account_rec['code'],
                'name': account_rec['name'],
                'level': account_rec['level'],
                'debit': account_rec['debit'],
                'credit': account_rec['credit'],
                'ytd_debit': account_rec['ytd_debit'],
                'ytd_credit': account_rec['ytd_credit'],
                'balance': account_rec['balance'],
                'parent_id': account_rec['parent_id'],
                'bal_type': '',
            }
            if disp_acc == 'movement':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['ytd_credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['ytd_debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    if account_rec['type'] != 'view':
                        self.result_acc.append(res)
                        self.sum_debit += account_rec['debit']
                        self.sum_credit += account_rec['credit']
                        self.ytd_sum_debit += account_rec['ytd_debit']
                        self.ytd_sum_credit += account_rec['ytd_credit']
            elif disp_acc == 'not_zero':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    if account_rec['type'] != 'view':
                        self.result_acc.append(res)
                        self.sum_debit += account_rec['debit']
                        self.sum_credit += account_rec['credit']
                        self.ytd_sum_debit += account_rec['ytd_debit']
                        self.ytd_sum_credit += account_rec['ytd_credit']
            else:
                if account_rec['type'] != 'view':
                    self.result_acc.append(res)
                    self.sum_debit += account_rec['debit']
                    self.sum_credit += account_rec['credit']
                    self.ytd_sum_debit += account_rec['ytd_debit']
                    self.ytd_sum_credit += account_rec['ytd_credit']
            if account_rec['child_id']:
                for child in account_rec['child_id']:
                    _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        date_from = date_to = False
        if form and form.get('period_id'):
            account_period = self.pool.get('account.period').browse(self.cr, self.uid, form.get('period_id')[0])
            date_from = account_period.date_start
            date_to = account_period.date_stop
        ctx.update({'date_from': date_from, 'date_to': date_to})
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        for acc in accounts:
            ctx.update({'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')})
            acc_ytd_data = obj_account.read(self.cr, self.uid, [acc['id']], ['debit','credit','balance'], ctx)
            acc.update({
                'ytd_credit': acc_ytd_data[0].get('credit') or 0.0,
                'ytd_debit': acc_ytd_data[0].get('debit') or 0.0
            })

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        return self.result_acc

    def get_sum_debit(self):
        return self.sum_debit or 0.0
    def get_sum_credit(self):
        return self.sum_credit or 0.0
    def get_sum_ytd_debit(self):
        return self.ytd_sum_debit or 0.0
    def get_sum_ytd_credit(self):
        return self.ytd_sum_credit or 0.0

report_sxw.report_sxw('report.account.trial.balance', 'account.account', 'addons/sg_account_report/report/trial_balance.rml', parser=account_balance, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
