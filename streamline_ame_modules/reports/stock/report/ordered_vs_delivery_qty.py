# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_report_ordered_vs_delivery_qty(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(wrapped_streamline_ame_report_ordered_vs_delivery_qty, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data_summary':self._get_data_summary,
        })

    def _get_data_summary(self, form):
        a = form['date_start']
        b = form['date_end']
        
        self.cr.execute('''
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
        ''',(a, b))
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_ordered_vs_delivery_qty(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_ordered_vs_delivery_qty'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_ordered_vs_delivery_qty'
    _wrapped_report_class = wrapped_streamline_ame_report_ordered_vs_delivery_qty

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
