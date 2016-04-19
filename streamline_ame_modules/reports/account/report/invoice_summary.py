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
        SELECT to_char(ai.date_invoice, 'dd/MM/yyyy') inv_date,
            ai."number" inv_no,
            pp.default_code stock_code,
            pt.name item_name,
            pt.description item_decs,
                substring(sl.complete_name FROM (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_stock,
                rp.name co_name,
                  substring((
                        SELECT string_agg(sp.name, ', ')
                    FROM sale_order so
                    INNER JOIN  sale_order_line sol on so.id = sol.order_id
                    INNER JOIN  procurement_group pg on so.procurement_group_id = pg.id
                    INNER JOIN  stock_picking sp on pg.id = sp.group_id
                    WHERE sol.product_id = ail.product_id
                    ), 2, 1000) do_name,
                 po.name po_name,
                 SUM(ail.price_unit) unit_price,
                 SUM(ail.quantity) qty,
                 SUM(ail.price_subtotal) as amount,
                 SUM(0.07 * ail.price_subtotal) as gst,
                 SUM(ail.price_subtotal + 0.07 * ail.price_subtotal) as total, project.name
                FROM account_invoice_line ail
                INNER JOIN  account_invoice ai on ai.id = ail.invoice_id
                INNER JOIN  product_product pp on ail.product_id = pp.id
                INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                INNER JOIN  purchase_invoice_rel pir on pir.invoice_id = ai.id
                INNER JOIN  purchase_order po on pir.purchase_id = po.id
                INNER JOIN  purchase_order_line pol on po.id = pol.order_id and pol.product_id = ail.product_id
                INNER JOIN  stock_move sm on sm.purchase_line_id = pol.id and ail.product_id = sm.product_id
                INNER JOIN  stock_location sl on sl.id = sm.location_dest_id
                INNER JOIN  res_partner rp on po.partner_id = rp.id
                LEFT JOIN streamline_ame_project_project project on po.project_no = project.id
                WHERE ai.type='in_invoice'
                and ai.state='paid'
                and ai.date_invoice::DATE BETWEEN %s::DATE and %s::DATE
            GROUP BY ai.date_invoice, ai."number", pp.default_code, pt.name, pt.description, sl.complete_name, rp.name, ail.product_id, po.name, project.name
                order by project.name, inv_no desc

        ''',(a, b))
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_invoice_summary(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_streamline_ame_invoice_summary'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_streamline_ame_invoice_summary'
    _wrapped_report_class = wrapped_streamline_ame_report_invoice_summary

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
