# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_report_inventory_listing(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(wrapped_streamline_ame_report_inventory_listing, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data_report':self._get_data_report,
        })

    def _get_data_report(self):
        company_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id.id
        self.cr.execute('''
        WITH  vendor_info AS (
            SELECT MAX(to_char(tpo.date_order, 'dd/MM/yyyy')) as date_order, rp.name vendor, sq.product_id
            FROM stock_quant sq
            INNER JOIN stock_quant_move_rel rel on rel.quant_id = sq.id
            INNER JOIN stock_move stkm on stkm.id = rel.move_id
            INNER JOIN purchase_order_line tpol on stkm.purchase_line_id = tpol.id
            INNER JOIN purchase_order tpo on tpol.order_id = tpo.id
            INNER JOIN res_partner rp on tpo.partner_id = rp.id and rp.supplier = 't'
            WHERE sq.company_id = %s
            group by 2,3)

        SELECT v.date_order, pp.default_code, pt.name, pt.description, pu.name uom, v.vendor
        FROM product_product pp
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        INNER JOIN product_uom pu on pt.uom_id = pu.id
        LEFT JOIN vendor_info v on v.product_id = pp.id
        WHERE pt.company_id = %s or pt.company_id is null
        ORDER BY pp.default_code
        '''%(company_id, company_id))
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_inventory_listing(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_inventory_listing'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_inventory_listing'
    _wrapped_report_class = wrapped_streamline_ame_report_inventory_listing

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
