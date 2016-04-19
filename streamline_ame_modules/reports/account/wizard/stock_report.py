# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp.addons.streamline_ame_modules.reports.streamline import REPORT_FORMAT


class streamline_ame_report_wizard_stock_report(models.TransientModel):
    _name = 'streamline.ame.report.wizard.stock.report'
    
    report_month = fields.Selection([
                        ('01','January'), 
                        ('02','February'), 
                        ('03','March'), 
                        ('04','April'), 
                        ('05','May'), 
                        ('06','June'),
                        ('07','July'), 
                        ('08','August'), 
                        ('09','September'), 
                        ('10','October'), 
                        ('11','November'), 
                        ('12','December')
                        ], 'Month', required=True)
    report_year = fields.Selection([
                        ('2016','2016'), 
                        ('2017','2017'), 
                        ('2018','2018'), 
                        ('2019','2019'), 
                        ('2020','2020'),
                        ('2021','2021'), 
                        ('2022','2022')
                        ], 'Year', required=True)
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
        res = self.read(cr, uid, ids, ['report_month', 'report_year', 'report_format'], context=context)
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
            return self.pool['report'].get_action(cr, uid, [], 'report_streamline_ame_stock_report_xls', data=datas, context=context)    
            
        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_stock_report', data=datas, context=context)

    
    