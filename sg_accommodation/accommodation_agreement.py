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

from openerp.osv import fields, osv
import time
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, ustr
from dateutil import relativedelta

class hr_employee(osv.Model):
    
    _inherit = 'hr.employee'
    
    _columns = {
        'accommodated':fields.boolean('Accommodated'),
        'pub_accommodation_history_ids' : fields.one2many('pub.accommodation.history','emp_id','Pub History'),
        'worker_location_id':fields.many2one('site.location', string='Worker Location'),
        'away':fields.boolean('Away'),
        'emp_away_history_ids':fields.one2many('emp.away.history','emp_id','Employee Away History'),
    }

class beds_beds(osv.Model):
    _name = 'beds.beds'
    
    _columns = {
        'name': fields.char('Name', size=240, required=True),
        'room_id': fields.many2one('room.room', 'Room', ondelete='cascade'),
        'employee_id':fields.many2one('hr.employee', 'Employee Name'),
    }    
    
    def check_emp(self, cr, uid, ids, context=None):
        for bed_emp in self.browse(cr, uid, ids, context=context):
            bed_emp_ids = bed_emp.employee_id.id
            if not bed_emp_ids:
                break
            bed_ids = self.search(cr, uid, [('employee_id', '=', bed_emp_ids)])
            if len(bed_ids) > 1 :
                raise osv.except_osv(_('Error!'),
                    _("No more bed is available for '%s' ") % \
                            (bed_emp.employee_id.name,))
        return True
     
    _constraints = [(check_emp, 'bed  limit exceeded !', ['employee_id'])]
    
class room_room(osv.Model):
    _name = 'room.room'
    
    def _beds_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        total_capacity = 0.0
        for rec in self.browse(cr, uid, ids, context=context):
            emp_bed = 0.0
            for bed in rec.bed_ids:
                if not bed.employee_id:
                    emp_bed += 1
            res[rec.id] = emp_bed
        return res
    
    _columns = {
         'name': fields.char('Name', size=240, required=True),
         'bed_ids': fields.one2many('beds.beds', 'room_id', 'Beds'),
         'available_beds':fields.function(_beds_available, string='Available Beds', type='integer'),
         'accommodation_id':fields.many2one('accommodation.accommodation', 'Accommodation', ondelete='cascade'),
         'visa_quota_ids': fields.one2many('visa.quota', 'room_id', 'Visa Quota', ondelete='cascade'),
    }
    
    def check_bed_ids(self, cr, uid, ids, context=None):
        bed_obj = self.pool.get('beds.beds')
        visa_obj = self.pool.get('visa.quota')
        for rooms_rec in self.browse(cr, uid, ids, context=context):
            accomodation_id = rooms_rec.accommodation_id and rooms_rec.accommodation_id.id or False
            if not accomodation_id:
                break
            room_ids = self.search(cr, uid, [('accommodation_id', '=', rooms_rec.accommodation_id.id)], context=context)
            beds = 0
            for f_room in self.browse(cr, uid, room_ids, context=context):
                beds += len(f_room.bed_ids)
            if beds > rooms_rec.accommodation_id.maximum_capacity:
                raise osv.except_osv(_('Error!'),
                    _("Maximum Capacity Exceeded for room '%s'!") % (rooms_rec.name))
            for bed in rooms_rec.bed_ids:
                if not bed.employee_id:
                    continue
                emp_nation_id = bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.id or False
                visa_ids = visa_obj.search(cr, uid, [('nationality_id', '=', emp_nation_id), ('room_id', '=', bed.room_id.id)], context=context)
                if not visa_ids:
                    raise osv.except_osv(_('Error!'),
                    _("No Visa Quota allocated for '%s' ") % \
                            (bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.name or False,))
                number_of_quota = 0.0
                for visa in visa_obj.browse(cr, uid, visa_ids, context=context):
                    number_of_quota = visa.quota_available
                if number_of_quota < 0.0:
                    raise osv.except_osv(_('Error!'),
                             _("Visa Quota limit exceed for '%s' ") % \
                        (bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.name or False,))

#                nationality_id = bed.employee_id and bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.id or False
#                visa_ids = visa_obj.search(cr, uid, [('nationality_id', '=', nationality_id), ('room_id', '=', bed.room_id.id)], context=context)
#                for visa_line in visa_obj.browse(cr, uid, visa_ids, context=context):
#                    number_of_quota += visa_line.quota_available
#                if not visa_ids:
#                    raise osv.except_osv(_('Error!'),
#                    _("No Visa Quota allocated for '%s' ") % \
#                            (bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.name or False,))
#                if number_of_quota < 0.0:
#                    raise osv.except_osv(_('Error!'),
#                             _("Visa Quota limit exceed for '%s' ") % \
#                        (bed.employee_id.emp_country_id and bed.employee_id.emp_country_id.name or False,))
            stay_capacity = rooms_rec.accommodation_id and rooms_rec.accommodation_id.stay_capacity or False
            if stay_capacity < 0:
                raise osv.except_osv(_('Error!'),
                     _("Stay Capacity limit exceed!"))
        return True

    _constraints = [
        (check_bed_ids, 'Visa Quota limit exceed!', ['bed_ids']),
    ]

class visa_quota(osv.Model):
    _name = 'visa.quota'
    
    def get_quota_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            reserv_bed = 0
            for bed_line in rec.room_id.bed_ids:
                if bed_line.employee_id and bed_line.employee_id.emp_country_id.id\
                and rec.nationality_id.id == bed_line.employee_id.emp_country_id.id:
                    reserv_bed += 1
            res[rec.id] = rec.number_of_quota - reserv_bed
        return res
    
    _rec_name = 'nationality_id'
    
    _columns = {
        'nationality_id': fields.many2one('res.country', 'Nationality'),
        'number_of_quota': fields.integer('Total', size=40, digits=(10, 2)),
        'quota_available':fields.function(get_quota_available, string='Available', type='integer'),
        'accommodation_id':fields.many2one('accommodation.accommodation', 'Accommodation', ondelete='cascade'),
        'room_id':fields.many2one('room.room','Room',ondelete='cascade'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
       for rec in self.browse(cr, uid, ids, context=context):
           if rec.number_of_quota == rec.quota_available:
               return super(visa_quota, self).unlink(cr, uid, ids, context=context)
           else:
               raise osv.except_osv(_('Warning!'), _('You cannot delete quota that is already assigned. !'))

    
    def check_quota_avail(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            room_rec=rec.room_id
            if not rec.room_id:
                break
            acco_ids = self.search(cr, uid, [('room_id', '=', room_rec.id)], context=context)
            total = 0
            for acco_val in self.browse(cr, uid, acco_ids, context=context):
                total += acco_val.number_of_quota
                if total > acco_val.room_id.available_beds:
                    return False
        return True

    _constraints = [
        (check_quota_avail, 'Maximum Capacity exceeded for allotting quota!', ['number_of_quota']),
    ]

class accommodation_accommodation(osv.Model):
    _name = 'accommodation.accommodation'
    
    def _get_occupied(self, cr, uid, ids, name, args, context=None):
        res = {}
        bed_obj = self.pool.get('beds.beds')
        for acc in self.browse(cr, uid, ids, context=context):
            bed_occupy = bed_obj.search(cr, uid, [('room_id.accommodation_id', '=', acc.id), ('employee_id', '!=', False)], context=context, count=True)
            res[acc.id] = bed_occupy
        return res
    
    def _get_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        bed_obj = self.pool.get('beds.beds')
        for acc in self.browse(cr, uid, ids, context=context):
            bed_avail = bed_obj.search(cr, uid, [('room_id.accommodation_id', '=', acc.id), ('employee_id', '=', False)], context=context, count=True)
            res[acc.id] = bed_avail
        return res
    
    def _cal_tenure_duration(self, cr, uid, ids, date_start, date_end, context=None):
        total = 0.0
        res = {}
        for date in self.browse(cr, uid, ids, context=context):
            dt_st = date.date_start
            dt_en = date.date_end
            
            if dt_st and dt_en:
                date1 = datetime.strptime(dt_st, DEFAULT_SERVER_DATE_FORMAT)
                date2 = datetime.strptime(dt_en, DEFAULT_SERVER_DATE_FORMAT)
                r = (date2 - date1)
                days_total = r.days
                years = days_total / 365
                rem_days = days_total % 365
                months = rem_days / 30
                tenure_str = ''
                if years:
                    tenure_str += ustr(years) + " Year(s)"
                if months:
                    if years:
                        tenure_str += " "
                    tenure_str += ustr(months) + " Month(s)"
                res[date.id] = tenure_str
        return res
                
    def cal_total_amount(self, cr, uid, ids, ser_and_cons, fur_and_fit, other_charges, context=None):
        total = 0.0
        res = {}
        for amt in self.browse(cr, uid, ids, context=context):
            if amt.ser_and_cons or amt.fur_and_fit or amt.other_charges or amt.rent:
                total = float(amt.ser_and_cons) + float(amt.fur_and_fit) + float(amt.other_charges) + float(amt.rent)
                res[amt.id] = total 
        return res
    
    def cal_rent_divide(self,cr,uid,ids,fields, arg,context=None):
        res = {}
        for amt in self.browse(cr,uid,ids,context=context):
            amount = 0.0
            if amt.rent and amt.maximum_capacity:
                amount=round(float(amt.rent) / float(amt.maximum_capacity),2)
                split_amount = str(amount).split('.')
                if split_amount:
                    if int(split_amount[1]) != 0 and int(split_amount[1]) <= 50:
                        res[amt.id] = split_amount[0] + '.50'
                    else:
                        res[amt.id] = round(amount)
        return res
              
    _columns = {
        'accommodation_id' : fields.integer('Accommodation Id'),
        'active':fields.boolean('Active', help='The active field which denotes the active accommodation'),
        'name':fields.char('Description', help='Description of Accommodation!'),
        'land_lord_id':fields.many2one('res.partner', 'LandLord'),
        'address_id': fields.many2one('res.partner', 'Location Address'),
        'paying_comp_id': fields.many2one('res.company', 'Tenant'),
        'rent': fields.float('Rent', digits=(10, 2)),
        'rental_pax': fields.integer('Rental Pax', digits=(5, 2)),
        'maximum_capacity': fields.integer('Maximum Capacity', digits=(10, 2)),
        'stay_capacity':fields.function(_get_available, string='Available', type='integer'),
        'occupied':fields.function(_get_occupied, string="Occupied", type='integer'),
        'employee_deduction': fields.float('Employee Deduction(%)', digits=(10, 2)),
        'company_deduction': fields.float('Company Deduction(%)', digits=(10, 2)),
        'room_ids': fields.one2many('room.room', 'accommodation_id', 'Rooms'),
        'date_start':fields.date("Date Start"),
        'date_end':fields.date("Date End"),
        'type':fields.many2one('accommodation.type' , 'Accommodation Type'),
        'amenities_ids' : fields.many2many('amenities.amenities', 'rel_amenities', 'acco_amenities', 'amenities_id', 'Amenities'),
        'security_ids' : fields.many2many('security.security', 'rel_security', 'acco_security', 'security_id', 'Security'),
        'exclusion_ids': fields.many2many('amenities.amenities', 'rel_exclusion', 'acco_sid', 'exclusion_id', 'Exclusion'),
        'payment_term_id' : fields.many2one('account.payment.term', 'Terms of Payment'),
        'premises' : fields.char('Use of Premises', size=128),
        'stamp_fees' : fields.char('Stamp Fees', size=128),
        'deposit' : fields.float('Deposit', digits=(10, 2)),
        'change_of_worker' : fields.integer('Change of Worker', help='Days written notice in advance'),
        'termination' : fields.integer('Termination', help='Days written notice for termination'),
        'liabilities' : fields.text('Liabilities'),
        'tenure' :fields.function(_cal_tenure_duration, string='Tenure', type='char'),
        'rcb_no' :fields.char('RCB NO'),
        'block_no' :fields.char('Block No'),
        'ser_and_cons' : fields.float('Service & Conservancy', digits=(10, 2)),
        'fur_and_fit' :fields.float('Furniture & Fittings', digits=(10, 2)),
        'other_charges' :fields.float('Other Charges', digits=(10, 2)),
        'total_amount' :fields.function(cal_total_amount, string='Total Amount per unit'),
        'agent' : fields.boolean("Agent"),
        'agent_id': fields.many2one('res.partner', "Agent Address"),
        'designation' : fields.char('Designation', size=24),
        'll_responsible' : fields.char('Landlord Responsible', size=32),
        'nric_no' : fields.char('NRIC No', size=24),
        'll_witness' : fields.char('Landlord Witness', size=32),
        'witness_nric_no' : fields.char('NRIC No', size=24),
        'ten_responsible' : fields.char('Tenant Responsible', size=32),
        'nric_no_ten' : fields.char('NRIC No', size=24),
        'ten_witness' : fields.char('Tenant Witness', size=32),
        'witness_nric_no_ten' : fields.char('NRIC No', size=24),
        'corres_address' : fields.boolean("Same as Registered Address"),
        'corress_address_id': fields.many2one('res.partner', "Correspondence Address"),
        'admin_fees': fields.float('Administration Fee'),
        'reference_no': fields.char('Reference No'),
        'history_ids':fields.one2many('accommodation.history', 'accommodation_id', 'Accommodation History'),
        'state':fields.selection([('draft', 'Draft'), ('open', 'Open'), ('expired', 'Expired'), ('waiting', 'Waiting for Renewal'), ('renewed', 'Renewed')], 'State'),
        'visa_quota_ids':fields.one2many('visa.quota', 'accommodation_id', 'Visa Quota', ondelete='cascade'),
        'pub_history_ids':fields.one2many('pub.history', 'accommodation_id', 'Pub History', ondelete='cascade'),
        'rent_per_pax':fields.function(cal_rent_divide, string='Rent Per Pax'),
    }
    _defaults = {
        'state': 'draft',
        'active': True
    }
    
    def confirm_accommodation(self, cr, uid, ids, context=None):
        """
        This method is used to confirm the accommodation
        ------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        """
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        return True
    
    def expire_accommodation(self, cr, uid, ids, context=None):
        """
        This method is used to expire the accommodation
        ------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        """
        self.write(cr, uid, ids, {'state':'expired'}, context=context)
        return True
    
    def draft_accommodation(self, cr, uid, ids, context=None):
        """
        This method is used to set the accommodation as draft
        -----------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        """
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True
    
    def request_renew_accommodation(self, cr, uid, ids, context=None):
        """
        This method is used to request the renewal of accommodation
        ------------------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        """
        self.write(cr, uid, ids, {'state':'waiting'}, context=context)
        return True
    
    def renew_accommodation(self, cr, uid, ids, context=None):
        """
        This method is used to request the renewal of accommodation
        ------------------------------------------------------------
        @param self : object pointer
        @param cr : database cursor
        @param uid : current logged in user
        @param ids : identifier(s) of current record(s)
        @param context : standard dictionary
        """
        self.write(cr, uid, ids, {'state':'renewed'}, context=context)
        return True
    
    def check_date_format(self, cr, uid, ids, date_start, date_end, context=None):
        res = {}
        if date_start and date_end:
            s_date = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT)
            e_date = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT)
            
            if s_date > e_date:
                res.update({'date_start':False , 'date_end':False})
                warning = {
                           'message': _('Start date must be less than end date')
                           }
                return {'value':res, 'warning':warning}
            return res
    
    def check_maximum_capacity(self, cr, uid, ids, context=None):
        for acc in self.browse(cr, uid, ids, context=context):
            no_of_beds = 0
            for room in acc.room_ids:
                no_of_beds += len(room.bed_ids)
            no_visa_ids = 0
            for visa in acc.visa_quota_ids:
                no_visa_ids += visa.number_of_quota
            if no_visa_ids > acc.maximum_capacity or no_of_beds > acc.maximum_capacity:
                return False
        return True
        
    _constraints = [
        (check_maximum_capacity, _('Maximum Capacity Must be greater or equal to number of Beds and number of Visa Quota !'), ['maximum_capacity']),
    ]
    
class res_partner(osv.Model):
    
    _inherit = 'res.partner'
    
    _columns = {
        'landlord':fields.boolean('Landlord', help='Is this a landlord of a property?'),
        'location':fields.boolean('Location', help='Is this address an Accommodation Location?'),
    }    

class res_company(osv.Model):
    
    _inherit = 'res.company'
    
    _columns = {
        'tenant':fields.boolean('Tenant', help='Is this company a tenant or not?')
    }

class amenities_amenities(osv.Model):
    _name = "amenities.amenities"
    
    _columns = {
                'name' : fields.char('Name'),
                'code' : fields.char('Code'),
                
    }
    
class security_security(osv.Model):
    _name = "security.security"
    
    _columns = {
                'name' : fields.char('Name'),
                'code' : fields.char('Code'),
                'price' : fields.float('Price'),
    }
    
class accommodation_type(osv.Model):
    
    _name = 'accommodation.type'
    
    _columns = {
              
        'name':fields.char('Name'),
        'code':fields.char('Code'),
              }

class accommodation_history(osv.Model):
    
    _name = 'accommodation.history'
    
    _rec_name = 'bed_id'
    
    _columns = {
        'bed_id':fields.many2one('beds.beds', 'Bed'),
        'room_id':fields.many2one('room.room', 'Room'),
        'accommodation_id':fields.many2one('accommodation.accommodation', 'Accommodation'),
        'date':fields.datetime('Date'),
        'country_id':fields.many2one('res.country', 'Country'),
        'employee_id':fields.many2one('hr.employee', 'Employee'),
        'type':fields.selection([('vacant', 'Vacant'), ('occupy', 'Occupy')], 'Type')
    }

class pub_accommodation_history(osv.Model):
    
    _name = 'pub.accommodation.history'
    
    _columns = {
    'year_emp':fields.char('Year'),
    'emp_id' : fields.many2one('hr.employee', 'Employee'),
    'date':fields.date('Date'),
    'month_emp':fields.selection([('1', 'Jan'), ('2', 'Feb'),('3', 'Mar'),('4', 'Apr'),('5', 'May'),('6', 'June')
                                                          ,('7', 'July'),('8', 'Aug'),('9', 'Sep'),('10', 'Oct'),('11', 'Nov'),('12', 'Dec')], 'Month'),
    'rent' : fields.float('Rent'),
    'pub_amount_emp' : fields.float('Pub Amount'),
    'accommodation_id':fields.many2one('accommodation.accommodation', 'Accommodation'),
    }

class pub_history(osv.Model):
    
    _name = 'pub.history'
    
    _columns = {
    'month':fields.selection([('1', 'Jan'), ('2', 'Feb'),('3', 'Mar'),('4', 'Apr'),('5', 'May'),('6', 'June')
                                                          ,('7', 'July'),('8', 'Aug'),('9', 'Sep'),('10', 'Oct'),('11', 'Nov'),('12', 'Dec')], 'Month'),
    'year':fields.char('Year'),
    'pub_amount':fields.float('Pub Amount'),
    'date' : fields.date('Date'),
    'accommodation_id':fields.many2one('accommodation.accommodation', 'Accommodation'),
    'pub_active':fields.boolean('Active')
    }
    
    def create(self,cr,uid,vals,context=None):
        res = super(pub_history,self).create(cr,uid,vals,context=context)
        pub_rec = self.browse(cr,uid,res,context=context)
        if not pub_rec.accommodation_id.state == 'open' and 'renewed':
            raise osv.except_osv(_('Error!'),
                 _("Cannot import pub file in  state '%s' for this accommodation")%(pub_rec.accommodation_id.state))
        return res
    
    def divide_pub(self,cr,uid,ids,context=None):
        acc_obj = self.pool.get('accommodation.accommodation')
        pub_acc_obj = self.pool.get('pub.accommodation.history')
        pub_brw = self.browse(cr,uid,ids,context=context)
        emp_list = []
        emp_bed = 0
        for acc_rec in acc_obj.browse(cr,uid,pub_brw.accommodation_id.id,context=context):
            for room in acc_rec.room_ids:
                for bed in room.bed_ids:
                    if bed.employee_id:
                        emp_bed += 1
                        emp_list.append(bed.employee_id.id)
            if emp_bed > 0:
                for emp in emp_list:
                    amount = pub_brw.pub_amount / emp_bed
                    amt=round(float(amount),2)
                    split_amount = str(amt).split('.')
                    if split_amount:
                        if int(split_amount[1]) != 0 and int(split_amount[1]) <= 50:
                            multiple_amount = split_amount[0] + '.50'
                        else:
                            multiple_amount = round(amount)
                    vals = {'emp_id':emp,'accommodation_id':pub_brw.accommodation_id.id,'rent':acc_rec.rent_per_pax,'pub_amount_emp':multiple_amount,'date':datetime.today()
                            ,'year_emp':str(pub_brw.year),'month_emp':str(int(pub_brw.month))}
                    pub_acc_obj.create(cr,uid,vals,context=context)
                    pub_brw.pub_active = True
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
