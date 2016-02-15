# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class gstf7(osv.osv_memory):
    _inherit = 'account.common.account.report'
    _name = 'account.gstreturnf7'

    def _get_tax_chart(self, cr, uid, context=None):
        """
            Return default Tax of Account Chart
        """
        chart_ids = self.pool.get('account.tax.code').search(cr, uid, [('parent_id','=', False)], context=context)
        return chart_ids and chart_ids[0] or False

    _columns = {
        'tax_chart_id': fields.many2one('account.tax.code', 'Chart of Taxes', domain = [('parent_id','=', False)]),
        'filter': fields.selection([('filter_no', 'No Filters'),('filter_period', 'Periods')], "Filter by", required=True),
        'box10': fields.float('Box10'),
        'box11': fields.float('Box11'),
        'box12': fields.float('Box12'),
    }

    _defaults = {
        'tax_chart_id': _get_tax_chart,
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = self.read(cr, uid, ids, context=context)[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'gstreturnf7.odoo',
            'datas': datas,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
