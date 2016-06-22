# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class clean_data(osv.osv_memory):
    _name = 'clean.data'

    _columns = {
        'product': fields.boolean('Remove Product'),
        'product_categ': fields.boolean('Remove Product Categories'),
    }


    def reset_number(self, cr, uid, ids, context=None):
        """ This method restes all running sequence """
        cr.execute("update ir_sequence set number_next=1;")
        ids = self.pool.get('ir.sequence').search(cr, uid, [])
        for element in self.pool.get('ir.sequence').browse(cr, uid, ids, context=context):
            if element.implementation == 'standard':
                statement = (
                    "ALTER SEQUENCE ir_sequence_%03d RESTART WITH 1"
                    % element.id)
                cr.execute(statement)
        return True
    
    def action_clean_data(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        try:
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'sale_order'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate sale_order cascade; DELETE FROM mail_message WHERE model = 'sale.order';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'account_voucher'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate account_voucher cascade; DELETE FROM mail_message WHERE model = 'account.voucher';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'purchase_order'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate purchase_order cascade; DELETE FROM mail_message WHERE model = 'purchase.order';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'stock_inventory'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate stock_inventory cascade; DELETE FROM mail_message WHERE model = 'stock.inventory';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'stock_pack_operation'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate stock_pack_operation cascade; DELETE FROM mail_message WHERE model = 'stock.pack.operation';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'stock_picking'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist:
                cr.execute("truncate stock_picking cascade; DELETE FROM mail_message WHERE model = 'stock.picking';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'account_invoice'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate account_invoice cascade; DELETE FROM mail_message WHERE model = 'account.invoice';")
            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'account_move'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate account_move cascade; DELETE FROM mail_message WHERE model = 'account.move';")

            is_exist = cr.execute('''SELECT EXISTS (
                                    SELECT 1
                                    FROM   information_schema.tables
                                    WHERE  table_schema = 'public'
                                    AND    table_name = 'pos_session'
                                    );''')
            is_exist = cr.dictfetchall()
            if is_exist and is_exist[0]['exists']:
                cr.execute("truncate pos_session cascade; DELETE FROM mail_message WHERE model = 'pos.session';")

            if obj.product_categ or obj.product:
                cr.execute('''SELECT EXISTS (
                                        SELECT 1
                                        FROM   information_schema.tables
                                        WHERE  table_schema = 'public'
                                        AND    table_name = 'product_template'
                                        );''')
                is_exist = cr.dictfetchall()
                if is_exist and is_exist[0]['exists']:
                    cr.execute("truncate product_template cascade; DELETE FROM mail_message WHERE model = 'product.template' or model = 'product.product';")
            if obj.product_categ:
                cr.execute('''SELECT EXISTS (
                                        SELECT 1
                                        FROM   information_schema.tables
                                        WHERE  table_schema = 'public'
                                        AND    table_name = 'product_category'
                                        );''')
                is_exist = cr.dictfetchall()
                if is_exist and is_exist[0]['exists']:
                    cr.execute("truncate product_category cascade; DELETE FROM mail_message WHERE model = 'product.category'")

            self.reset_number(cr, uid, ids, context)
        except Exception, e:
            _logger.error(e)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
