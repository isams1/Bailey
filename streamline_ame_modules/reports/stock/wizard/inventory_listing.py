# -*- coding: utf-8 -*-

from openerp import models, fields

class streamline_ame_report_wizard_inventory_listing(models.TransientModel):
    _name = 'streamline.ame.report.wizard.inventory.listing'
    
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
        res = self.read(cr, uid, ids, [], context=context)
        res = res and res[0] or {}
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_inventory_listing', data=datas, context=context)