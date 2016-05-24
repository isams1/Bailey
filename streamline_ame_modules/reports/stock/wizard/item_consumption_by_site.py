from openerp import models, fields

class streamline_ame_report_wizard_item_consumption_by_site(models.TransientModel):
    _name = 'streamline.ame.report.wizard.item.consumption.by.site'

    def _get_location(self):
        location = self.env['stock.location'].search([('name', 'in', ('371', '378'))])
        if location:
            return location.ids
        return []

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    location_ids = fields.Many2many('stock.location', 'consumption_by_site_loation_rel', 'report_id', 'location_id',
                                    string='Locations', domain=[('usage', '=', 'internal')], default=_get_location)

    
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
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]

        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_item_consumption_by_site', data=datas, context=context)