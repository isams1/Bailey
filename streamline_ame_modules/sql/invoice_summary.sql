select to_char(ai.date_invoice, 'dd/MM/yyyy') inv_date, ai."number" inv_no, pp.default_code stock_code, pt.description item_decs, sl.complete_name location_stock,
	rp.name co_name, sp.name do_name, po.name po_name, pol.price_unit item_price
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
left join stock_quant_move_rel sqmr on sm.id = sqmr.move_id
left JOIN stock_quant sq on sqmr.quant_id = sq.id
LEFT JOIN stock_pack_operation spo on sq.lot_id = spo.lot_id
left join (
	SELECT picking_id, po.id
  FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
  WHERE po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
  GROUP BY picking_id, po.id
) tmp_picking_po on tmp_picking_po.picking_id = sp.id
left join purchase_order po on tmp_picking_po.id = po.id
left join purchase_order_line pol on po.id = pol.order_id and ail.product_id = pol.id
where ai.type='out_invoice'
and ai.state='paid'
order by do_name