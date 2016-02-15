from openerp.osv import osv,fields


class add_nationality(osv.TransientModel):
    
    _name = 'add.nationality'
    
    _columns = {
        'room_id':fields.many2one('room.room','Room'),
        'country_id':fields.many2one('res.country','Country'),
        'availability':fields.float('Availability'),
    }
    
    def add_country_avail(self, cr, uid, ids, context=None):
        """
        This method is used to add/update national availability for rooms
        -----------------------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context: standard dictionary
        @return True
        """
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        vis_obj = self.pool.get('visa.quota')
        vis_ids = vis_obj.search(cr, uid, [('nationality_id','=',wiz_rec.country_id.id),('room_id','=',wiz_rec.room_id.id)], context=context)
        if vis_ids:
            vis_brws=vis_obj.browse(cr,uid,vis_ids,context=context)
            for vis_rec in vis_brws:
                quota=vis_rec.number_of_quota+wiz_rec.availability
                vis_obj.write(cr, uid, vis_ids, {'number_of_quota':quota}, context=context)
        else:
            vis_vals = {
                'room_id':wiz_rec.room_id.id,
                'number_of_quota':wiz_rec.availability,
                'accommodation_id':wiz_rec.room_id.accommodation_id.id,
                'nationality_id':wiz_rec.country_id.id
            }
            vis_obj.create(cr, uid, vis_vals, context=context)
        return True
    