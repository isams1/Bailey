# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class clean_data(osv.osv_memory):
    _name = 'clean.data'
    
    def action_clean_data(self, cr, uid, ids, context=None):
        try:
            cr.execute("delete from sale_order")
            cr.execute("delete from account_voucher")
            cr.execute("delete from account_invoice")
            cr.execute("delete from account_move")
            cr.execute("delete from purchase_order")
            cr.execute("delete from stock_move")
            cr.execute("delete from stock_inventory")
            cr.execute("delete from stock_quant")
            cr.execute("delete from stock_pack_operation")
            cr.execute("delete from stock_picking")
        except Exception, e:
            _logger.error(e)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
