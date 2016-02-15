# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class account_gstreturn(osv.osv_memory):
    _inherit = 'account.common.account.report'
    _name = 'account.gstreturn'

    _columns = {
        'year_id': fields.many2one('account.fiscalyear', 'Fiscal year'),
        'tax_chart_id': fields.many2one('account.tax.code', 'Chart of Taxes', domain=[('parent_id', '=', False)]),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_period', 'Periods')], "Filter by", required=True),
        'box10': fields.float('Box10'),
        'box11': fields.float('Box11'),
        'box12': fields.float('Box12'),
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = self.read(cr, uid, ids, context=context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gstreturn',
            'datas': datas,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
