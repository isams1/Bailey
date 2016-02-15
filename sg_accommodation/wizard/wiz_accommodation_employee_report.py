from openerp.osv import osv, fields
from openerp import models, fields, api, _
import tempfile
import xlwt
from xlwt import Workbook
from StringIO import StringIO
import base64

class wiz_accommodation_employee_report(models.TransientModel):
    
    _name = 'wiz.accommodation.employee.report'
    
    accommodation_ids = fields.Many2many('accommodation.accommodation', 'wiz_accommodation_rel', 'accommodation_id', 'wizard_id', 'Accommodation')
    
    @api.multi
    def print_report(self):
        
        cr, uid, context = self.env.args
        context = dict(context)
        
        fl = StringIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header1 = xlwt.easyxf('font: bold on, height 200;borders : top thin, bottom thin, left thin, right thin;align: wrap off , vert centre, horiz left;')
        head_bck_yellow = xlwt.easyxf('font: bold on, height 220;borders : top thin, bottom thin, left thin, right thin;pattern: pattern solid, fore_colour light_yellow;align: wrap on , vert centre, horiz center;')
        header2 = xlwt.easyxf('font: height 180;borders : top thin, bottom thin, left thin, right thin;align: wrap on , vert centre, horiz left;')
        
        wiz_rec = self.browse(self._ids[0])
        comp_obj = self.env['res.company']
        acc_obj = self.env['accommodation.accommodation']
        bed_obj = self.env['beds.beds']
        companies = {}
        dict_val = {}
        company_ids = comp_obj.search([('tenant', '=', True)])
        for comp in company_ids:
            companies.update(dict([(comp.id, comp.code)]))
        new_lst = []
        for accom in wiz_rec.accommodation_ids:
            accommodation = False
            accom_dict = {'sr_no' : accom.name,
                    'acc_name' : '',
                    'country':'',
                    'tenant':'',
                    'max':'',
                    'occupied':'',
                    'available':'',
                    'accom' : 1,
                    'room' : 0}
            count = 0
            for room in accom.room_ids:
                count += 1
                visa_dict = {}
                
                for visa in room.visa_quota_ids:
                    company_dict = {}
                    country_comp_total = 0
                    for company_id in company_ids:
                        visa_nat_id = visa.nationality_id.id
                        bed_ids_filled = bed_obj.search([
                            ('room_id', '=', room.id),
                            ('employee_id', '!=', False),
                            ('employee_id.company_id', '=', company_id.id),
                            ('employee_id.emp_country_id', '=', visa_nat_id)
                        ])
                        country_comp_total += len(bed_ids_filled)
                        company_dict[companies.get(company_id.id)] = len(bed_ids_filled)
                    company_dict['total'] = country_comp_total
                    visa_dict[visa.nationality_id.name] = company_dict
                new_dict = {
                    'sr_no' : count,
                    'acc_name' : room.name,
                    'landlord':'',
                    'tenant':accom.paying_comp_id.code,
                    'max':len(room.bed_ids),
                    'occupied':len(room.bed_ids) - room.available_beds,
                    'available':room.available_beds,
                    'accom' : 0,
                    'room' : 1
                    }
                flag = 0
                for key, val in visa_dict.iteritems():
                    if not accommodation:
                        new_lst.append(accom_dict)
                        accommodation = True
                    if not flag:
                        new_dict['country'] = key
                        new_dict.update(val)
                        flag = True
                        new_lst.append(new_dict)
                    else:
                        country_dict = {}
                        country_dict['country'] = key
                        country_dict.update(val)
                        country_dict.update(
                                {'sr_no' : '',
                                'acc_name' : '',
                                'landlord':'',
                                'tenant':'',
                                'max':'',
                                'occupied':'',
                                'available':'',
                                'accom' : 0,
                                'room' : 0
                                })
                        new_lst.append(country_dict)
                country_lst_len = len(new_lst)
        datas = {
            'form': new_lst,
            }
    
        row = 0
        worksheet.col(3).width = 5000
        
        worksheet.write_merge(row, row + 1, 0, 0, 'S.No', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 1, 1, 'COM', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 2, 2, 'Location / Address', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 3, 3, 'Nationality', head_bck_yellow)
        worksheet.write_merge(row, row , 4, 9, 'Occupant (Company Wise)', head_bck_yellow)
        worksheet.write(row + 1, 4, 'CM', head_bck_yellow)
        worksheet.write(row + 1, 5, 'DV', head_bck_yellow)
        worksheet.write(row + 1, 6, 'SME', head_bck_yellow)
        worksheet.write(row + 1, 7, 'UM', head_bck_yellow)
        worksheet.write(row + 1, 8, 'SBT', head_bck_yellow)
        worksheet.write(row + 1, 9, 'TOTAL', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 10, 10, 'Stay Men', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 11, 11, 'Max. Capacity', head_bck_yellow)
        worksheet.write_merge(row, row + 1, 12, 12, 'Vacancies', head_bck_yellow)
    
        row += 2
        for lst in new_lst:
            if lst['accom'] == True:
                worksheet.write_merge(row, row + 1, 0, 12, lst['sr_no'], header1)
                row += 2
                if lst['room'] == True:
                    worksheet.write(row, 0, lst['sr_no'] , header2)
                    worksheet.write(row, 1, lst['tenant'] , header2)
                    worksheet.write(row, 2, lst['acc_name'] , header2)
                    worksheet.write(row, 3, lst['country'] , header2)
                    worksheet.write(row, 4, lst.get('CM') , header2)
                    worksheet.write(row, 5, lst.get('DV') , header2)
                    worksheet.write(row, 6, lst.get('SME') , header2)
                    worksheet.write(row, 7, lst.get('UM') , header2)
                    worksheet.write(row, 8, lst.get('SBT') , header2)
                    worksheet.write(row, 9, lst.get('total') , header2)
                    worksheet.write(row, 10, lst['occupied'] , header2)
                    worksheet.write(row, 11, lst['max'] , header2)
                    worksheet.write(row, 12, lst['available'] , header2)
                    
                    row += 1
                
            if lst['accom'] == False:
                worksheet.write(row, 0, lst['sr_no'] , header2)
                worksheet.write(row, 1, lst['tenant'] , header2)
                worksheet.write(row, 2, lst['acc_name'] , header2)
                worksheet.write(row, 3, lst['country'] , header2)
                worksheet.write(row, 4, lst.get('CM') , header2)
                worksheet.write(row, 5, lst.get('DV') , header2)
                worksheet.write(row, 6, lst.get('SME') , header2)
                worksheet.write(row, 7, lst.get('UM') , header2)
                worksheet.write(row, 8, lst.get('SBT') , header2)
                worksheet.write(row, 9, lst.get('total') , header2)
                worksheet.write(row, 10, lst['occupied'] , header2)
                worksheet.write(row, 11, lst['max'] , header2)
                worksheet.write(row, 12, lst['available'] , header2)
                
                row += 1
                
        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'acco.location.report',
                'target': 'new',
                'context': ctx,
                }

class acco_location_report(models.TransientModel):
    
    _name = 'acco.location.report'
        
    @api.model
    def default_get(self, fields):
        if self._context is None:
            context = {}
            
        context = self._context
        res = super(acco_location_report, self).default_get(fields)
        res.update({'name': 'Locationwise.xls'})
        if self._context.get('file'):
            res.update({'file': context['file']})
        return res

    file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    @api.multi
    def action_back(self):
        if self._context is None:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.accommodation.employee.report',
            'target': 'new',
        }


