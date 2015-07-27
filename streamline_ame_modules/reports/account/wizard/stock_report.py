# -*- coding: utf-8 -*-

from openerp import models, fields

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
                        ('2012','2012'), 
                        ('2013','2013'), 
                        ('2014','2014'),
                        ('2015','2015'), 
                        ('2016','2016'), 
                        ('2017','2017'), 
                        ('2018','2018'), 
                        ('2019','2019'), 
                        ('2020','2020'),
                        ('2021','2021'), 
                        ('2022','2022')
                        ], 'Year', required=True)
    
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
        res = self.read(cr, uid, ids, ['report_month', 'report_year'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_invoice_summary', data=datas, context=context)

    
    