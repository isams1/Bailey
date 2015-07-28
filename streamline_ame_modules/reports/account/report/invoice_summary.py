# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_report_invoice_summary(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(wrapped_streamline_ame_report_invoice_summary, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_invoice_summary':self._get_invoice_summary,
        })

    def _get_invoice_summary(self, form):
        a = form['date_start']
        b = form['date_end']
        
        self.cr.execute('''
        select pp.id, to_char(ai.date_invoice, 'dd/MM/yyyy') inv_date, ai."number" inv_no, pp.default_code stock_code, pt.description item_decs, tmp_picking_po.picking_id,
            substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_stock, rp.name co_name,
          (
                select max(sp.name)
                from sale_order so
                inner join sale_order_line sol on so.id = sol.order_id
                inner join procurement_group pg on so.procurement_group_id = pg.id
                inner join stock_picking sp on pg.id = sp.group_id
            where sol.product_id = ail.product_id
            ) do_name, 
          po.name po_name, pol.price_unit unit_price,
          (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_dest_id = sm.location_id and product_qty is not null group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_id = sm.location_id and product_qty is not null group by product_id), 0)) as qty),
        
            pol.price_unit * (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_dest_id = sm.location_id and product_qty is not null group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_id = sm.location_id and product_qty is not null group by product_id), 0)) as qty) as amount,
        
            0.07 * pol.price_unit * (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_dest_id = sm.location_id and product_qty is not null group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_id = sm.location_id and product_qty is not null group by product_id), 0)) as qty) as gst,
        
           (
                    pol.price_unit * (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_dest_id = sm.location_id and product_qty is not null group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_id = sm.location_id and product_qty is not null group by product_id), 0)) as qty)
                ) - 
            (
                    0.07 * pol.price_unit * (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_dest_id = sm.location_id and product_qty is not null group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = sm.product_id and state in ('done', 'transit') and location_id = sm.location_id and product_qty is not null group by product_id), 0)) as qty)
                ) as total
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join purchase_invoice_rel pir on pir.invoice_id = ai.id
        inner join purchase_order po on pir.purchase_id = po.id
        inner join purchase_order_line pol on po.id = pol.order_id
        left join (
            SELECT max(picking_id) picking_id, po.id po_id
          FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
          WHERE po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
          GROUP BY po.id
        ) tmp_picking_po on tmp_picking_po.po_id = po.id
        inner join stock_move sm on sm.picking_id = tmp_picking_po.picking_id and ail.product_id = sm.product_id
        inner join stock_location sl on sl.id = sm.location_dest_id
        inner join res_partner rp on po.partner_id = rp.id
        where ai.type='in_invoice'
        and ai.state='paid'
        and ai.date_invoice::DATE BETWEEN %s::DATE and %s::DATE
        order by inv_no
        ''',(a, b))
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_invoice_summary(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_invoice_summary'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_invoice_summary'
    _wrapped_report_class = wrapped_streamline_ame_report_invoice_summary

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
