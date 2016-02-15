from openerp import fields, models, api, _
from datetime import datetime
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import tempfile
import StringIO
import base64
import tempfile
import csv
import xlrd
from xlrd import open_workbook
from openerp.exceptions import except_orm, Warning, RedirectWarning

class add_pub(models.TransientModel):
    
    _name = 'add.pub'
    
    date = fields.Date(string='Date', default=datetime.strftime(datetime.now(), DEFAULT_SERVER_DATE_FORMAT))
    pub_file = fields.Binary(string='Import PUB')
    datas_fname = fields.Char('Filename')
    
    @api.multi
    def add_pub(self):
        pub_history_obj = self.env['pub.history']
        acc_obj = self.env['accommodation.accommodation']
        cr, uid, context = self.env.args
        context = dict(context)
        for data in self:
            filename_str = str(data.datas_fname)
            split_file = filename_str.split('.')
            if not data.pub_file:
                raise Warning(_('Please select PUB file to proceed.'))
            if not filename_str[-4:] == ".xls":
                raise Warning(_('Select .xls file only'))
            csv_data = base64.decodestring(data.pub_file)
            temp_path = tempfile.gettempdir()

            fp = open(temp_path + '/xsl_file.xls', 'wb+')
            fp.write(csv_data)
            fp.close()
            wb = open_workbook(temp_path + '/xsl_file.xls')
            
            header_list = []
            for sheet in wb.sheets():
                for rownum in range(sheet.nrows):
                    header_list.append({rownum : sheet.row_values(rownum)})
            pub_vals = {}
            for dict_new in header_list[1:]:
                for key , val in dict_new.iteritems():
                    acc_brw = acc_obj.browse(int(val[0]))
                    if acc_brw.state == 'open' or acc_brw.state == 'renewed':
                        pub_ids = pub_history_obj.search([('accommodation_id', '=', int(val[0])),
                                                    ('date', '=', data.date),
                                                    ('month', '=', str(int(val[1]))),
                                                    ('year', '=', int(val[2])),
                                                    ('pub_amount', '=', float(val[3]))])
                        if not pub_ids:
                            pub_vals = {
                               'accommodation_id':int(val[0]),
                               'date':data.date,
                               'month':str(int(val[1])),
                               'year':int(val[2]),
                               'pub_amount':float(val[3])
                            }
                            pub_history_obj.create(pub_vals)
                    else:
                        continue
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pub.import.notification',
                'target': 'new',
                'context': context,
                }
    
class pub_import_notification(models.TransientModel):
    
    
    _name = 'pub.import.notification'
