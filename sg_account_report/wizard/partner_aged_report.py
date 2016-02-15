from openerp.osv import fields, osv
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_aged_trial_balance_inherited(osv.osv_memory):
    
    _inherit = 'account.aged.trial.balance'
    
    _columns = {
        'partner_ids':fields.many2many('res.partner','aged_partners','cust_id','customer_id','Customers'),
    }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
        cur_rec= self.read(cr,uid,ids)[0]
        res={'partner_ids': cur_rec['partner_ids']}
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.aged_trial_balance_inherited',
            'datas': data
        }

account_aged_trial_balance_inherited()