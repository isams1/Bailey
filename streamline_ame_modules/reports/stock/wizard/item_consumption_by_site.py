from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from openerp.osv.fields import datetime as datetime_field
from datetime import datetime

class streamline_ame_report_wizard_item_consumption_by_site(models.TransientModel):
    _name = 'streamline.ame.report.wizard.item.consumption.by.site'

    def _get_location(self):
        location = self.env['stock.location'].search([('name', 'in', ('371', '378'))])
        if location:
            return location.ids
        return []

    date_from1 = fields.Date('Date From', required=True)
    date_from = fields.Datetime('Date From', required=True)
    date_to1 = fields.Date('Date To', required=True)
    date_to = fields.Datetime('Date To', required=True)
    location_ids = fields.Many2many('stock.location', 'consumption_by_site_loation_rel', 'report_id', 'location_id',
                                    string='Locations', domain=[('usage', '=', 'internal')], default=_get_location)

    def _convert_timezone(self, date, format_string='%Y-%m-%d %H:%M:%S'):
        import logging
        logging.info(date)
        date = datetime.strptime(date, format_string)

        new_date = datetime_field.context_timestamp(self._cr, self._uid, timestamp=date, context=self._context)
        new_date = datetime.strptime(new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
        duration = new_date - date
        seconds = duration.total_seconds()
        hours = seconds // 3600

        date = date + relativedelta(hours=hours)
        return date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.onchange('date_from1')
    def onchange_date_from1(self):
        if not self.date_from1:
            self.date_from = False
        else:
            self.date_from = self._convert_timezone('%s 00:00:00'%str(self.date_from1))

    @api.onchange('date_to1')
    def onchange_date_to1(self):
        if not self.date_to1:
            self.date_to = False
        else:
            self.date_to = self._convert_timezone('%s 23:59:59'%str(self.date_to1))

    
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
        print '================', res
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]

        return self.pool['report'].get_action(cr, uid, [], 'streamline_ame_modules.report_streamline_ame_item_consumption_by_site', data=datas, context=context)