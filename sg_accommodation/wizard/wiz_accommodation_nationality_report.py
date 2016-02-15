from openerp.osv import osv, fields
from openerp import models, fields, api, _
import tempfile
import xlwt
from xlwt import Workbook
from StringIO import StringIO
import base64

class wiz_accommodation_nationality_report(models.TransientModel):
    
    _name = 'wiz.accommodation.nationality.report'
    
    @api.multi
    def _get_nationality_ids(self):
        self._cr.execute('select distinct(v.nationality_id),c.name from visa_quota v, res_country c where v.nationality_id=c.id')
        res = self._cr.fetchall()
        country_ids = [tpl[0] for tpl in res]
        return [(6, 0, country_ids)]
    
    nationality_ids = fields.Many2many('res.country', 'wiz_country_rel', 'nationality_id', 'wizard_id', 'Nationality', default=_get_nationality_ids)
    
    @api.multi
    def check_report(self):
        cr, uid, context = self.env.args
        context = dict(context)
        
        fl = StringIO()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 180;')
        header1 = xlwt.easyxf('font: bold on, height 200;borders : top thin, bottom thin, left thin, right thin;align: wrap off , vert centre, horiz center;')
        header2 = xlwt.easyxf('font: bold on, height 180;borders : top thin, bottom thin, left thin, right thin;align: wrap on , vert centre, horiz center;')
        align_left = xlwt.easyxf('font: height 200, bold on, name Arial, colour_index periwinkle;borders : top thin, bottom thin, left thin, right thin; align: wrap on,vert centre, horiz left;')
        align_border = xlwt.easyxf('font: height 180, name Arial, colour_index black;borders : top thin, bottom thin, left thin, right thin; align: wrap on,vert centre, horiz left;')
        
        wiz_rec = self.browse(self._ids[0])
        bed_obj = self.env['beds.beds']
        visa_obj = self.env['visa.quota']
        room_obj = self.env['room.room']
        list_new = []
        country_dict = {}
        for country in wiz_rec.nationality_ids:
            acco_dict = {}
            country_id = country.id
            visa_ids = visa_obj.search([('nationality_id', '=', country_id)])
            for visa in visa_ids:
                acco_name = visa.accommodation_id.name
                acc_dict = {}
                company_dict = {}
                visa_total = visa.number_of_quota
                visa_avail = visa.quota_available
                visa_occupied = visa_total - visa_avail
                country_comp_total = 0
                room_ids = room_obj.search([('accommodation_id', '=', visa.accommodation_id.id)])
                for room in room_ids:
                    room_id = room
                    occupied_beds = bed_obj.search([('employee_id.emp_country_id', '=', visa.nationality_id.id),
                            ('employee_id', '!=', False),
                            ('room_id', '=', room_id.id)])
                    occu_beds = []
                    counter = 0
                    for bed in occupied_beds:
                        bed_dict = {}
                        counter += 1
                        bed_dict['sr_no'] = counter or ''
                        bed_dict['id_no'] = bed.employee_id.identification_id or ''
                        bed_dict['bed_no'] = bed.name or ''
                        bed_dict['name'] = bed.employee_id.name or ''
                        bed_dict['wp_number'] = bed.employee_id.wp_number or ''
                        bed_dict['com'] = bed.employee_id.company_id.name or ''
                        bed_dict['dialect'] = bed.employee_id.dialect or ''
                        bed_dict['country'] = False
                        bed_dict['location'] = False
                        bed_dict['room'] = False
                        bed_dict['bold'] = False
                        
                        occu_beds.append(bed_dict)
                    if occu_beds:
                        company_dict[room.name] = occu_beds
                    
                if acco_name in acco_dict.keys():
                    acco_dict[acco_name]['room_list'].append(company_dict)
                else:
                    acco_dict[acco_name] = {'room_list':[company_dict]}
            country_dict[country.name] = acco_dict
        final_dict = {}
        final_list = []
        for con_key, con_val in country_dict.iteritems():
            country = False
            con_dict = {
                'sr_no':con_key,
                'bed_no':'',
                'id_no' : '',
                'name':'',
                'wp_number':'',
                'com' : '',
                'dialect' : '',
                'country' : True,
                'location' : False,
                'room' : False,
                'bold' : True
            }

            for loc_key, loc_val in con_val.iteritems():
                location = False
                room_bold_dict = {
                    'sr_no':loc_key,
                    'bed_no':'',
                    'id_no' : '',
                    'name':'',
                    'wp_number':'',
                    'com' : '',
                    'dialect' : '',
                    'country' : False,
                    'location' : True,
                    'room' : False,
                    'bold' : True
                    }
                for room in loc_val.get('room_list', [{}]):
                    for room_key, room_value in room.iteritems():
                        room_dict = {
                        'sr_no':room_key,
                        'bed_no': '',
                        'id_no' : '',
                        'name':'',
                        'wp_number':'',
                        'com' : '',
                        'dialect' : '',
                        'country' : False,
                        'location' : False,
                        'room' : True,
                        'bold' : True
                        }
                        if not country:
                            final_list.append(con_dict)
                            country = True
                        if not location:
                            final_list.append(room_bold_dict)
                            location = True
                        final_list.append(room_dict)
                        final_list += room_value

        row = 1
        for lst in final_list:
            if lst['country'] == True:
                worksheet.write_merge(row, row + 1, 0, 3, 'LIST OF "' + lst['sr_no'] + '" WORKERS ACCOMMODATION', align_left)
                row += 2
            if lst['location'] == True:
                worksheet.write(row, 0, 'LOCATION :' , header1)
                worksheet.write(row, 1, lst['sr_no'] , align_left) 
                row += 1
            if lst['room'] == True:
                worksheet.write(row, 0, 'ROOM :' , header1)
                worksheet.write(row, 1, lst['sr_no'], align_left)
                row += 2

                worksheet.write_merge(row, row + 1, 0, 0, 'NO', header2)
                worksheet.write_merge(row, row + 1, 1, 1, 'BED NO', header2)
                worksheet.write_merge(row, row + 1, 2, 2, 'CODE NO', header2)
                worksheet.write_merge(row, row + 1, 3, 3, 'NAME', header2)
                worksheet.write_merge(row, row + 1, 4, 4, 'W/P NUMBER', header2)
                worksheet.write_merge(row, row + 1, 5, 5, 'COM', header2)
                worksheet.write_merge(row, row + 1, 6, 6, 'DIALECT', header2)
                worksheet.write_merge(row, row + 1, 7, 7, 'SITE', header2)
                worksheet.write_merge(row, row + 1, 8, 8, 'Date of Application', header2)
                worksheet.write_merge(row, row + 1, 9, 9, 'REMARKS', header2)
                row += 2
            if lst['bold'] == False:
                worksheet.write(row, 0, lst['sr_no'], align_border)
                worksheet.write(row, 1, lst['bed_no'], align_border)
                worksheet.write(row, 2, lst['id_no'], align_border)
                worksheet.write(row, 3, lst['name'], align_border)
                worksheet.write(row, 4, lst['wp_number'], align_border)
                worksheet.write(row, 5, lst['com'], align_border)
                worksheet.write(row, 6, lst['dialect'], align_border)
                worksheet.write(row, 7, 'static', align_border)
                worksheet.write(row, 8, 'static', align_border)
                worksheet.write(row, 9, 'static', align_border)
                row += 2

        workbook.save(fl)
        fl.seek(0)
        buf = base64.encodestring(fl.read())
        ctx = dict(context)
        ctx.update({'file': buf})
        
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'acco.nationality.report',
                'target': 'new',
                'context': ctx,
                }

class acco_nationality_report(models.TransientModel):
    
    _name = 'acco.nationality.report'
        
    @api.model
    def default_get(self, fields):
        if self._context is None:
            context = {}
            
        context = self._context
        res = super(acco_nationality_report, self).default_get(fields)
        res.update({'name': 'Nationalitywise.xls'})
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
            'res_model': 'wiz.accommodation.nationality.report',
            'target': 'new',
        }
