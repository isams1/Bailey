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

class wiz_create_room_bed(models.TransientModel):
    _name = 'wiz.create.room.bed'
    _description = 'Wizard Create Room/Beds'
    
    room = fields.Char('Room', help='Name of room')
    beds = fields.Integer('Number Beds', help='Number of beds created for room')
    
    def create_room(self, cr, uid, ids, context=None):
        '''
        This method creates number of beds in a room given by the user
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Wizard ID
        @param context : standard dictionary
        @return True
        '''
        if not context:
            context = {}
        room_obj = self.pool.get('room.room')
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        beds = []
        bed_no = 0
        for bed in range(wiz_rec.beds):
            bed_no += 1
            beds.append((0, 0, {'name' : str(bed_no)}))
        room_vals = {
             'name' : wiz_rec.room,
             'bed_ids' : beds,
             'accommodation_id' : context.get('active_id', False)
        }
        room_obj.create(cr, uid, room_vals, context=context)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: