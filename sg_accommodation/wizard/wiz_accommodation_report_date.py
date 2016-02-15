from openerp import models, fields,_,api
import xlwt
from xlwt import Workbook,easyxf, Style, Formula, Pattern
from StringIO import StringIO
import base64
from datetime import datetime
from openerp.tools import misc
class acc_report_date(models.TransientModel):
    
    _name = 'acc.report.date'
    
    date = fields.Date('Date')
    
    @api.multi
    def print_report(self):
        cr,uid,context=self.env.args
        if context is None:
            context = {}  
        context = dict(context)
        fl = StringIO()
        wbk = xlwt.Workbook(encoding='utf-8')
        sheet = wbk.add_sheet('Accommodation Report',cell_overwrite_ok=True)
        count_style = xlwt.easyxf('font: bold 1,height 200; borders: top double, bottom double, right double,left double, bottom_color black;align: wrap off , horiz center;')
        font_style_bold = xlwt.easyxf('font: bold 1,height 200;align: wrap off , horiz left;')
        font_style_center_only = xlwt.easyxf('font: height 200;align: wrap off , horiz center;')
        border_style = xlwt.easyxf('font: height 200; borders: right double,left double, bottom_color black;align: wrap off , horiz center;')
        color_style_title = xlwt.easyxf('font: bold 1,height 300, bold on, name Arial, colour_index black;borders : top double, bottom double, right double,left double, bottom_color black; pattern: pattern solid, fore_colour coral; align: wrap on,vert centre, horiz left;align: wrap off , horiz center;')
        color_style2 = xlwt.easyxf('font: bold 1,height 200, bold on, name Arial, colour_index black;borders : top double, bottom double, right double,left double, bottom_color black; pattern: pattern solid, fore_colour ice_blue; align: wrap on,vert centre, horiz left;align: wrap off , horiz center;')
        color_style_total = xlwt.easyxf('font: bold 1,height 220, bold on, name Arial, colour_index black;borders : top double, bottom double, right double,left double, bottom_color black; pattern: pattern solid, fore_colour coral; align: wrap on,vert centre, horiz left;align: wrap off , horiz center;')
        sheet.row(0).height = 800
        sheet.col(0).width = 10000
        sheet.col(1).width = 5000
        sheet.col(2).width = 6000
        sheet.col(3).width = 11000
        today_date = datetime.today().strftime('%d %B %Y')
        today = " VACANCIES OF ACCOMMODATION (AS OF " + today_date + ")" 
        sheet.write_merge(0, 0, 0, 3, today,color_style_title)
        sheet.write(1,0,'LOCATION',color_style2)
        sheet.write(1,1,'ROOM NO.',color_style2)
        sheet.write(1,2,'NO.OF VACANCY',color_style2)
        sheet.write(1,3,'NATIONALITY',color_style2)
#        context.update({'report': 'Accommodation Report'})
        
        hist_obj = self.env['accommodation.history']
        acc_obj = self.env['accommodation.accommodation']
        
        for wiz_rec in self:
            date = wiz_rec.date
            accom_ids = acc_obj.search([])
            total_vacancy = 0.0
            row=2
            for accom in acc_obj.browse([accom_id.id for accom_id in accom_ids]):
                sheet.write(row,0,accom.name,font_style_bold)
                for room in accom.room_ids:
                    sheet.write(row,1,room.name,border_style)
                    for vis in room.visa_quota_ids:
                        his_args = [
                            ('country_id','=',vis.nationality_id.id),
                            ('room_id','=',room.id),
                            ('date','<=',date + " 23:59:59"),
                        ]
                        his_args_occupied =  his_args + [('type','=','occupy')]
                        hist_ids_occupied = hist_obj.search(his_args_occupied)
                        his_args_vacant =  his_args + [('type','=','vacant')]
                        hist_ids_vacant = hist_obj.search(his_args_vacant)
                        no_of_vac = vis.number_of_quota - len(hist_ids_occupied)+ len(hist_ids_vacant)
                        sheet.write(row,2,no_of_vac,border_style)
                        total_vacancy+=no_of_vac
                        sheet.write(row,3,vis.nationality_id.name,border_style)
                        row+=1
        sheet.write(row,0,"TOTAL",color_style_total)
        sheet.write(row,1,"",color_style_total)
        sheet.write(row,2,total_vacancy,color_style_total)
        sheet.write(row,3," ",color_style_total)
        wbk.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        self.env.args = cr,uid,misc.frozendict(context)
        try:
            form_id = self.env['ir.model.data'].get_object_reference('accommodation', 'wiz_dwnld_acc_report_form_dt')[1]
        except ValueError:
            form_id = False
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'accom.dwnld.datewise.report',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
        }

class accom_dwnld_datewise_report(models.TransientModel):
    _name = 'accom.dwnld.datewise.report'

    file = fields.Binary('File')
    file_name = fields.Char(string='File Name', size=64)
    
    @api.model
    def default_get(self,fields):
        cr,uid,context=self.env.args
        if context is None:
            context = {}
        context = dict(context)
        res = super(accom_dwnld_datewise_report, self).default_get(fields)
#        if context.get('report', False):
        res.update({'file_name': 'Accommodation Date Wise'+'.xls'})
        if context.get('file'):
            res.update({'file': context['file']})
        return res
    
    @api.multi
    def action_back(self):
        cr,uid,context=self.env.args
        if context is None:
            context = {}
        context = dict(context)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acc.report.date',
            'target': 'new',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: