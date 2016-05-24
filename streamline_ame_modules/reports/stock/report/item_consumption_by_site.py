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

    def _get_item_consumption_by_site(self, form, location_id, company_id):
        print location_id
        refund_ids = self._get_refund_location(form['location_ids'], location_id)
        print refund_ids
        select = ''
        refund_select = ''
        refund_sql = ''' '''
        remain = 'sum(COALESCE(X.in_qty - X.out_to_wh'
        for refund in refund_ids.keys():
            select += 'sum(COALESCE(X.out_to_%s, 0)) as  out_to_%s,'%(str(refund_ids[refund]), str(refund_ids[refund]))
            select += 'max(out_to_%s_date) as out_to_%s_date,'%(str(refund_ids[refund]), str(refund_ids[refund]))
            refund_select += ''' '' as out_to_%s_date, 0 as out_to_%s,'''%(str(refund_ids[refund]), str(refund_ids[refund]))
            remain += ' - X.out_to_%s'%str(refund_ids[refund])

            refund2_select = ''
            for refund2 in refund_ids.keys():
                if refund == refund2:
                    refund2_select += ''' to_char(max(sm.date), 'dd-MM-yyyy') as out_to_%s_date, sum(COALESCE(sm.product_qty, 0)) as out_to_%s, '''%(str(refund_ids[refund]), str(refund_ids[refund]))
                else:
                    refund2_select += ''' '' as out_to_%s_date, 0 as out_to_%s,'''%(str(refund_ids[refund]), str(refund_ids[refund]))

            refund_sql += '''
                UNION
        -- out to 378
                        (SELECT sm.product_id, pt.name, pp.default_code, pt.description, pc.name as categ,
                    ''  as in_date, ''  as out_to_wh_date, %s
                    0 as in_qty, 0 as out_to_wh
                    FROM stock_move sm
                    INNER JOIN  product_product pp on sm.product_id = pp.id
                    INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                    INNER JOIN  product_category pc on pt.categ_id = pc.id
                    WHERE sm.company_id = 1
                    AND sm.location_dest_id = %s and sm.location_id = %s
                    AND sm.product_id in
                    (
                        SELECT sq.product_id
                        FROM stock_quant sq
                        WHERE sq.lot_id is not null
                    )
                GROUP BY sm.product_id, pp.default_code, pt.name, pt.description, pc.name, sm.date
                        )
            '''%(refund2_select, refund, location_id)
        remain += ', 0)) as remain_qty,'

        sql = '''
            SELECT X.product_id, X.default_code, X.name, X.description, X.categ,

                    sum(COALESCE(X.in_qty, 0)) as stock_in,
                    sum(COALESCE(X.out_to_wh, 0)) as  out_to_wh,
                    %s
                    %s
                    max(out_to_wh_date) as out_to_wh_date,
                    max(in_date) as in_date

                FROM (
        -- in stock
                        (SELECT sm.product_id, pt.name, pp.default_code, pt.description, pc.name as categ,
                    to_char(max(sm.date), 'dd-MM-yyyy') as in_date, '' as out_to_wh_date, %s
                    sum(COALESCE(sm.product_qty, 0)) as in_qty, 0 as out_to_wh
                    FROM stock_move sm
                    INNER JOIN  product_product pp on sm.product_id = pp.id
                    INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                    INNER JOIN  product_category pc on pt.categ_id = pc.id
                    WHERE sm.company_id = %s
                    AND sm.location_dest_id = %s and sm.location_id <> %s
                    AND sm.product_id in
                    (
                        SELECT sq.product_id
                        FROM stock_quant sq
                        WHERE sq.lot_id is not null
                    )
                GROUP BY sm.product_id, pp.default_code, pt.name, pt.description, pc.name, sm.date
                )
                        UNION
        -- out to stock
                        (SELECT sm.product_id, pt.name, pp.default_code, pt.description, pc.name as categ,
                    '' as in_date, to_char(max(sm.date), 'dd-MM-yyyy') as out_to_wh_date, %s
                    0 as in_qty, sum(COALESCE(sm.product_qty, 0)) as out_to_wh
                    FROM stock_move sm
                    INNER JOIN  product_product pp on sm.product_id = pp.id
                    INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                    INNER JOIN  product_category pc on pt.categ_id = pc.id
                    WHERE sm.company_id = %s
                    AND sm.location_dest_id = 12 and sm.location_id = %s
                    AND sm.product_id in
                    (
                        SELECT sq.product_id
                        FROM stock_quant sq
                        WHERE sq.lot_id is not null
                    )
                GROUP BY sm.product_id, pp.default_code, pt.name, pt.description, pc.name, sm.date
                        )
                        %s
            ) as X

             GROUP BY X.product_id, X.default_code, X.name, X.description, X.categ
        '''%(select, remain, refund_select, company_id, location_id, location_id, refund_select, company_id, location_id, refund_sql)
        print sql
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_item_consumption_by_site(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_item_consumption_by_site'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_item_consumption_by_site'
    _wrapped_report_class = wrapped_streamline_ame_report_item_consumption_by_site

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
