# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp.addons.streamline_ame_modules.reports.__init__ import REPORT_FORMAT


class streamline_ame_report_wizard_invoice_summary(models.TransientModel):
    _name = 'streamline.ame.report.wizard.invoice.summary'

    date_start= fields.Date('Date Start', required=True, default=fields.Date.today)
    date_end= fields.Date('Date End', required=True, default=fields.Date.today)
    report_format= fields.Selection(REPORT_FORMAT, 'Report Format')
    
    _defaults = {
        'report_format': lambda *args: 'pdf',
    }
        
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
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'report_format'], context=context)
        res = res and res[0] or {}
        
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
            
        # get report_format
        if res.get('report_format', 'pdf') == 'xls':
            context['xls_export'] = 1
        
        if context.get('xls_export'):
            #return {'type': 'ir.actions.report.xml', 'report_name': 'report.streamline.ame.invoice.summary.xls', 'datas': datas}      
            context['data'] = datas      
            return self.pool['report'].get_action(cr, uid, [], 'report_streamline_ame_invoice_summary_xls', data=datas, context=context)
            
        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_invoice_summary', data=datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
