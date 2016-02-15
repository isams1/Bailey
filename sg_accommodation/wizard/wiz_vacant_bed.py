from openerp import fields, models,api,_
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

class wiz_vacant_bed(models.TransientModel):
    
    _name = 'wiz.vacant.bed'
    
    employee_id = fields.Many2one('hr.employee','Employee')
    room_id = fields.Many2one('room.room', 'Room')
    bed_id = fields.Many2one('beds.beds', 'Bed')
    
    @api.onchange('employee_id')
    def onchange_employee(self):
        """
        This method is used to identify the bed and room based on the 
        employee selected.
        ------------------------------------------------------------------
        @param self : object pointer
        @param return : True
        """
        cr, uid, context = self.env.args
        bed_obj = self.env['beds.beds']
        emp_id = self.employee_id.id
        if emp_id:
            #If employee is there fetch the related room and bed
            bed_id = bed_obj.search([('employee_id','=',self.employee_id.id),('room_id.accommodation_id','=',context.get('accommodation_id'))])
            if not bed_id:
                emp_name = self.employee_id.name
                raise ValidationError('The Employee is not accommodated here!' + emp_name)
            self.bed_id = bed_id.id
            self.room_id = bed_id.room_id.id
    
    def vacant_bed(self, cr, uid, ids, context=None):
        """
        This method is used to vacant the bed in a room in accommodation
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        @return True
        """
        if not context:
            context = {}
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        bed_obj = self.pool.get('beds.beds')
        history_obj = self.pool.get('accommodation.history')
        history_vals = {
            'bed_id': wiz_rec.bed_id.id,
            'room_id':wiz_rec.room_id.id,
            'accommodation_id':wiz_rec.room_id.accommodation_id.id,
            'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'employee_id':wiz_rec.bed_id.employee_id.id,
            'country_id':wiz_rec.bed_id.employee_id.emp_country_id.id,
            'type':'vacant',
        }
        # Make the bed Empty
        wiz_rec.bed_id.write({'employee_id':False})
        # Create History in Accommodation
        history_obj.create(cr, uid, history_vals, context=context)
        #Update Accomodated in Employee
        wiz_rec.employee_id.write({'accommodated':False})
        return True