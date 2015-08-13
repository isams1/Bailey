select Y.default_code, Y.description, 
            substring(Y.delivered_from from (length('Physical Locations / ') + strpos(Y.delivered_from, 'Physical Locations / '))) delivered_from, 
            substring(Y.delivered_to from (length('Physical Locations / ') + strpos(Y.delivered_to, 'Physical Locations / '))) delivered_to, 
            Y.delivered_date, COALESCE(Y.delivered_qty_to_site, 0) delivered_qty_to_site, Y.returned_date, COALESCE(Y.returned_qty_to_HQ, 0) returned_qty_to_hq
        FROM
        (
        select X.default_code, X.description, X.delivered_from,
        (
        select tsl.complete_name
        from stock_location tsl
        where tsl.id = X.location_dest_id
        ) delivered_to,
        (
        select sum(COALESCE(A.product_qty, 0))
        from
        (
        select DISTINCT tsm.*
        from stock_quant tsq
        inner join stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
        inner join stock_move tsm on tsm.id = tsqmr.move_id
        inner join stock_picking_type tspt on tsm.picking_type_id = tspt.id
        where tsq.lot_id is not null
        and tspt.code = 'internal'
        and tsq.product_id = X.product_id
        and tsm.location_id = X.location_id
        and tsm.location_dest_id = X.location_dest_id
        )A) delivered_qty_to_site,
        (
        select sum(COALESCE(A.product_qty,0))
        from
        (
        select DISTINCT tsm.*
        from stock_quant tsq
        inner join stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
        inner join stock_move tsm on tsm.id = tsqmr.move_id
        inner join stock_picking_type tspt on tsm.picking_type_id = tspt.id
        where tsq.lot_id is not null
        and tspt.code = 'internal'
        and tsq.product_id = X.product_id
        and tsm.location_id = X.location_dest_id
        and tsm.location_dest_id = X.location_id
        )A) returned_qty_to_HQ,
        (
        select to_char(max(A.date), 'dd-MM-yyyy')
        from
        (
        select DISTINCT tsm.*
        from stock_quant tsq
        inner join stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
        inner join stock_move tsm on tsm.id = tsqmr.move_id
        inner join stock_picking_type tspt on tsm.picking_type_id = tspt.id
        where tsq.lot_id is not null
        and tspt.code = 'internal'
        and tsq.product_id = X.product_id
        and tsm.location_id = X.location_id
        and tsm.location_dest_id = X.location_dest_id
        )A) delivered_date,
        (
        select to_char(max(A.date), 'dd-MM-yyyy')
        from
        (
        select DISTINCT tsm.*
        from stock_quant tsq
        inner join stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
        inner join stock_move tsm on tsm.id = tsqmr.move_id
        inner join stock_picking_type tspt on tsm.picking_type_id = tspt.id
        where tsq.lot_id is not null
        and tspt.code = 'internal'
        and tsq.product_id = X.product_id
        and tsm.location_id = X.location_dest_id
        and tsm.location_dest_id = X.location_id
        )A) returned_date
        from
        (
        select DISTINCT sm.product_id, pp.name_template, pp.default_code, pt.description, sm.location_id, sm.location_dest_id, sl.complete_name delivered_from
        from stock_move sm
        inner join stock_picking_type spt on sm.picking_type_id = spt.id
        inner join product_product pp on sm.product_id = pp.id
        inner JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join stock_location sl on sm.location_id = sl.id
        and spt.code = 'internal'
        where sm.location_id in
        (
        select spt.default_location_dest_id
        from stock_picking_type spt
        INNER JOIN stock_warehouse sw on spt.warehouse_id = sw.id
        where sw.company_id = 1
        and sw.partner_id = 1
        and spt.code = 'incoming'
        )
        and sm.product_id in
        (
        select sq.product_id
        from stock_quant sq
        where sq.lot_id is not null 
        ))X)Y
        where Y.delivered_qty_to_site is not null
        order by 1