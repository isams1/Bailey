import time
from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_report_item_consumption_by_site(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(wrapped_streamline_ame_report_item_consumption_by_site, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_item_consumption_by_site':self._get_item_consumption_by_site,
            'get_location': self._get_location,
            'get_refund_location': self._get_refund_location,
        })

    def _get_refund_location(self, location_ids, location_id):
        location_obj = self.pool.get('stock.location')
        lst_location = {}
        for location in location_obj.browse(self.cr, self.uid, location_ids):
            if location.id != location_id:
                lst_location.update({location.id: location.name})
        return lst_location

    def _get_location(self, location_id):
        return self.pool.get('stock.location').browse(self.cr, self.uid, location_id).name

    def _get_item_consumption_by_site(self, form, location_id):
        print form, location_id

        self.cr.execute('''
        select Y.default_code, Y.description, y.name,
            substring(Y.delivered_from from (length('Physical Locations / ') + strpos(Y.delivered_from, 'Physical Locations / '))) delivered_from, 
            substring(Y.delivered_to from (length('Physical Locations / ') + strpos(Y.delivered_to, 'Physical Locations / '))) delivered_to, 
            Y.delivered_date, COALESCE(Y.delivered_qty_to_site, 0) delivered_qty_to_site, Y.returned_date, COALESCE(Y.returned_qty_to_HQ, 0) returned_qty_to_hq
        FROM
            (SELECT X.default_code, X.name, X.description, X.delivered_from,
            X.delivered_to,
            sum(COALESCE(delivered.product_qty, 0)) as delivered_qty_to_site,
            sum(COALESCE(returned.product_qty, 0)) as  returned_qty_to_HQ,
            to_char(max(delivered.date), 'dd-MM-yyyy') as delivered_date,
            to_char(max(returned.date), 'dd-MM-yyyy') as returned_date
            FROM
            (
                SELECT DISTINCT sm.product_id, pp.name_template as name, pp.default_code, pt.description,
                spt.default_location_src_id as location_id, spt.default_location_dest_id as location_dest_id,
                location_src.complete_name delivered_from, location_dest.complete_name delivered_to
                FROM stock_move sm
                INNER JOIN  product_product pp on sm.product_id = pp.id
                INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                INNER JOIN  stock_picking_type spt on sm.picking_type_id = spt.id
                INNER JOIN  stock_location location_dest on location_dest.id = spt.default_location_dest_id
                INNER JOIN  stock_location location_src on location_src.id = spt.default_location_src_id
                WHERE spt.code = 'incoming'
                    AND sm.company_id = 1
                --product in warehouse
                AND sm.product_id in
                (
                    SELECT sq.product_id
                    FROM stock_quant sq
                    WHERE sq.lot_id is not null
                )
            ) as X
            LEFT JOIN
            (
                SELECT tsm.date, tsm.product_id, tsm.location_id, tsm.location_dest_id, tsm.id, tsm.product_qty
                FROM stock_quant tsq
                INNER JOIN  stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
                INNER JOIN  stock_move tsm on tsm.id = tsqmr.move_id
                GROUP BY tsm.date, tsm.product_id, tsm.location_id, tsm.location_dest_id, tsm.id

            ) AS delivered ON (delivered.product_id = X.product_id
                    AND delivered.location_id = X.location_id
                    AND delivered.location_dest_id = X.location_dest_id)
            LEFT JOIN
            (
                SELECT tsm.date, tsm.product_id, tsm.location_id, tsm.location_dest_id, tsm.id, tsm.product_qty
                FROM stock_quant tsq
                INNER JOIN  stock_quant_move_rel tsqmr on tsq.id = tsqmr.quant_id
                INNER JOIN  stock_move tsm on tsm.id = tsqmr.move_id
                GROUP BY tsm.date, tsm.product_id, tsm.location_id, tsm.location_dest_id, tsm.id

            ) AS returned ON (delivered.product_id = X.product_id
                    AND delivered.location_id = X.location_dest_id
                    AND delivered.location_dest_id = X.location_id)
        GROUP BY X.default_code, X.name, X.description, X.delivered_from, X.delivered_to)Y
            where Y.delivered_qty_to_site is not null
            order by 1
        ''')
        res = self.cr.dictfetchall()
        return []

class report_streamline_ame_item_consumption_by_site(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_item_consumption_by_site'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_item_consumption_by_site'
    _wrapped_report_class = wrapped_streamline_ame_report_item_consumption_by_site

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
