select pp.name_template prod_code, pt.description prod_description, po.name po_name, pol.product_qty po_qty, sum(sm.product_qty) received_qty,
    substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name 
from stock_move sm 
inner join purchase_order_line pol on sm.purchase_line_id = pol.id
inner join purchase_order po on pol.order_id = po.id
inner join stock_picking sp on sm.picking_id = sp.id
inner join product_product pp on sm.product_id = pp.id
inner join product_template pt on pp.product_tmpl_id = pt.id
inner join stock_location sl on sm.location_dest_id = sl.id
where sm.state = 'done'
and po.date_order::DATE BETWEEN %s::DATE and %s::DATE
group by 1,2,3,4,6
order by 3,1