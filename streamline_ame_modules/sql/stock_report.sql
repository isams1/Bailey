select X.product_name, to_char(X.date_invoice, 'DD-MM-YYYY') date_invoice, X.location_name project_no, X.units,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
		and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015') , 0))) stock_in,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015'), 0))) stock_out,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
    and product_qty is not null
    and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0) - 
	COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0)) as balance),
COALESCE((select max(value_float)
from ir_property
where name = 'standard_price'
and res_id = 'product.template,' || X.product_template_id), 0) unit_price_per_pc,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
		and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0) - 
	COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0)) as balance) *
COALESCE((select max(value_float)
from ir_property
where name = 'standard_price'
and res_id = 'product.template,' || X.product_template_id), 0) amount
from
(
select pu.name units, pt.id product_template_id, pp.id as product_id, pp.name_template as product_name, sl.id as location_id, substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name, max(ai.date_invoice) date_invoice
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join stock_location sl on sl.id = sm.location_id
where ai.type='in_invoice'
and ai.state='paid'
and sl."name" like '%Stock%'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
group by 1,2,3,4,5,6
) X
UNION ALL
select Y.product_name, Y.date_invoice, Y.partner_name, Y.units, Y.stock_in, Y.stock_out, Y.stock_in as balance, Y.unit_price_per_pc, Y.stock_in * Y.unit_price_per_pc amount  
FROM
(
select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
	COALESCE(sum(sm.product_qty), 0) stock_in, 0 stock_out, 
	COALESCE((select max(value_float)
	from ir_property
	where name = 'standard_price'
	and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join purchase_order_line pol on sm.purchase_line_id = pol.id
inner join purchase_order po on pol.order_id = po.id
inner join res_partner rp on po.partner_id = rp.id
where ai.type='in_invoice'
and ai.state='paid'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
and sm.purchase_line_id is not null
group by 1,2,3,4,5
) Y
union ALL
select X.product_name, X.date_invoice, X.partner_name, X.units, X.stock_in, X.stock_out, (X.stock_in - X.stock_out) as balance, X.unit_price_per_pc, (X.stock_in - X.stock_out) * X.unit_price_per_pc amount  
FROM
(
select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
	0 stock_in, COALESCE(sum(sm.product_qty), 0) stock_out, 
	COALESCE((select max(value_float)
	from ir_property
	where name = 'standard_price'
	and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join stock_picking sp on sm.picking_id = sp.id
inner join stock_picking_type spt on spt.id = sp.picking_type_id
inner join res_partner rp on sp.partner_id = rp.id
where ai.type='in_invoice'
and ai.state='paid'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
and spt.code = 'outgoing'
group by 1,2,3,4,5
) X
UNION ALL
select Z.product_name, null, null, null, sum(Z.stock_in), sum(Z.stock_out), sum(Z.stock_in) - sum(Z.stock_out), max(Z.unit_price_per_pc), (sum(Z.stock_in) - sum(Z.stock_out)) * max(Z.unit_price_per_pc)
from
(
select X.product_name, to_char(X.date_invoice, 'DD-MM-YYYY') date_invoice, X.location_name project_no, X.units,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
		and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015') , 0))) stock_in,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015'), 0))) stock_out,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
    and product_qty is not null
    and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0) - 
	COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0)) as balance),
COALESCE((select max(value_float)
from ir_property
where name = 'standard_price'
and res_id = 'product.template,' || X.product_template_id), 0) unit_price_per_pc,
(select (COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
		and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0) - 
	COALESCE((select sum(COALESCE(product_qty,0)) 
		from stock_move 
		where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
    and product_qty is not null and to_char(date_expected, 'MM-YYYY') = '05-2015' group by product_id), 0)) as balance) *
COALESCE((select max(value_float)
from ir_property
where name = 'standard_price'
and res_id = 'product.template,' || X.product_template_id), 0) amount
from
(
select pu.name units, pt.id product_template_id, pp.id as product_id, pp.name_template as product_name, sl.id as location_id, substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name, max(ai.date_invoice) date_invoice
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join stock_location sl on sl.id = sm.location_id
where ai.type='in_invoice'
and ai.state='paid'
and sl."name" like '%Stock%'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
group by 1,2,3,4,5,6
) X
UNION ALL
select Y.product_name, Y.date_invoice, Y.partner_name, Y.units, Y.stock_in, Y.stock_out, Y.stock_in as balance, Y.unit_price_per_pc, Y.stock_in * Y.unit_price_per_pc amount  
FROM
(
select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
	COALESCE(sum(sm.product_qty), 0) stock_in, 0 stock_out, 
	COALESCE((select max(value_float)
	from ir_property
	where name = 'standard_price'
	and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join purchase_order_line pol on sm.purchase_line_id = pol.id
inner join purchase_order po on pol.order_id = po.id
inner join res_partner rp on po.partner_id = rp.id
where ai.type='in_invoice'
and ai.state='paid'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
and sm.purchase_line_id is not null
group by 1,2,3,4,5
) Y
union ALL
select X.product_name, X.date_invoice, X.partner_name, X.units, X.stock_in, X.stock_out, (X.stock_in - X.stock_out) as balance, X.unit_price_per_pc, (X.stock_in - X.stock_out) * X.unit_price_per_pc amount  
FROM
(
select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
	0 stock_in, COALESCE(sum(sm.product_qty), 0) stock_out, 
	COALESCE((select max(value_float)
	from ir_property
	where name = 'standard_price'
	and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
from account_invoice ai
inner join account_invoice_line ail on ai.id = ail.invoice_id
INNER JOIN product_product pp on ail.product_id = pp.id
INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
inner join product_uom pu on pt.uom_id = pu.id
inner join stock_move sm on ail.product_id = sm.product_id
inner join stock_picking sp on sm.picking_id = sp.id
inner join stock_picking_type spt on spt.id = sp.picking_type_id
inner join res_partner rp on sp.partner_id = rp.id
where ai.type='in_invoice'
and ai.state='paid'
and sm."state" in ('transit', 'done')
and to_char(ai.date_invoice, 'MM-YYYY') = '05-2015'
and to_char(sm.date_expected, 'MM-YYYY') = '05-2015'
and spt.code = 'outgoing'
group by 1,2,3,4,5
) X
order by 1,2
) Z
GROUP BY product_name
order by 1,2