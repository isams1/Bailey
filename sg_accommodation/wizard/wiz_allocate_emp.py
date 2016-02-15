# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Serpent Consulting Services Pvt.Ltd. (<http://www.serpentcs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models,api,_
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
from openerp.exceptions import ValidationError

class wiz_allocate_emp(models.TransientModel):
    
    _name = 'wiz.allocate.emp'
    _description = 'Wizard Allocate Employee'
    
    employee_id = fields.Many2one('hr.employee', 'Employee')
    room_id = fields.Many2one('room.room', 'Room')
    bed_id = fields.Many2one('beds.beds', 'Bed')
    
    def allocate_emp(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        room_obj = self.pool.get('room.room')
        history_obj = self.pool.get('accommodation.history')
        room_obj.write(cr, uid, wiz_rec.room_id.id, {'bed_ids' : [(1, wiz_rec.bed_id.id, {'employee_id' : wiz_rec.employee_id.id})]}, context=context)
        if not wiz_rec.employee_id.emp_country_id:
            raise ValidationError('Please configure country in Employee!')
        history_vals = {
            'bed_id': wiz_rec.bed_id.id,
            'room_id':wiz_rec.room_id.id,
            'accommodation_id':wiz_rec.room_id.accommodation_id.id,
            'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'employee_id':wiz_rec.employee_id.id,
            'country_id':wiz_rec.employee_id.emp_country_id.id,
            'type':'occupy',
        }
        history_obj.create(cr, uid, history_vals, context=context)
        wiz_rec.employee_id.write({'accommodated':True})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: