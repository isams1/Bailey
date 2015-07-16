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
        select pp.id, to_char(ai.date_invoice, 'dd/MM/yyyy') inv_date, ai."number" inv_no, pp.default_code stock_code, pt.description item_decs, substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_stock,
		rp.name co_name, sp.name do_name, po.name po_name, pol.price_unit unit_price,
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
        inner join sale_order_invoice_rel soir on ai.id = soir.invoice_id
        inner join sale_order so on soir.order_id = so.id
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        inner join sale_order_line sol on so.id = sol.order_id and sol.product_id = ail.product_id
        inner join procurement_group pg on so.procurement_group_id = pg.id
        inner join stock_picking sp on pg.id = sp.group_id
        inner join stock_move sm on sm.picking_id = sp.id and ail.product_id = sm.product_id
        inner join stock_location sl on sl.id = sm.location_id
        inner join res_partner rp on so.partner_id = rp.id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        left JOIN
        (
            select move_id, max(quant_id) quant_id
          from stock_quant_move_rel  
          group by move_id
        ) tmp_sqmr on sm.id = tmp_sqmr.move_id
        left JOIN stock_quant sq on tmp_sqmr.quant_id = sq.id
        left join 
        (
            select spo.picking_id, spo.lot_id
            from stock_pack_operation spo
            inner join stock_picking sp1 on spo.picking_id = sp1.id
            inner join stock_picking_type spt on sp1.picking_type_id = spt.id and spt.code = 'incoming'
            where spo.lot_id is not null
        ) tmp_pack_op on tmp_pack_op.lot_id = sq.lot_id
        left join (
            SELECT picking_id, po.id
          FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
          WHERE po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
          GROUP BY picking_id, po.id
        ) tmp_picking_po on tmp_picking_po.picking_id = tmp_pack_op.picking_id
        left join purchase_order po on tmp_picking_po.id = po.id
        left join purchase_order_line pol on po.id = pol.order_id and ail.product_id = pol.product_id
        where ai.type='out_invoice'
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
