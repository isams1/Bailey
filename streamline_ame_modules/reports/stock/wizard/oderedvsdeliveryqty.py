# -*- coding: utf-8 -*-

from openerp import models, fields

class streamline_ame_report_wizard_ordered_vs_delivery_qty(models.TransientModel):
    _name = 'streamline.ame.report.wizard.ordered.vs.delivery.qty'

    date_start= fields.Date('Date Start', required=True, default=fields.Date.today)
    date_end= fields.Date('Date End', required=True, default=fields.Date.today)    
        
    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_ordered_vs_delivery_qty', data=datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
