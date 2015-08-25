# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.report import report_sxw

class wrapped_streamline_ame_purchase_order(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(wrapped_streamline_ame_purchase_order, self).__init__(cr, uid, name, context=context)
        self.index = 0
        self.localcontext.update({
                'get_contacts':self.get_contacts,
            })

    def get_contacts(self,partner, need_data):
        final = ""
        partner_obj = self.pool.get('res.partner')
        for partner_id in partner_obj.browse(self.cr, self.uid, [partner.id]):
            for line in partner_id.child_ids:
                if need_data == "phone":
                    final = line.phone or partner_id.phone
                elif need_data == "mobile":
                    final = line.mobile or partner_id.mobile
                elif need_data == "fax":
                    final = line.fax or partner_id.fax
                elif need_data == "email":
                    final = line.email or partner_id.email
                return final
            
        return final

class report_streamline_ame_purchase_order(osv.AbstractModel):
    _name = 'report.streamline_ame_modules.report_purchase_order'
    _inherit = 'report.abstract_report'
    _template = 'streamline_ame_modules.report_purchase_order'
    _wrapped_report_class = wrapped_streamline_ame_purchase_order
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
