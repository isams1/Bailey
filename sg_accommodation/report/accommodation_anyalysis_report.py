# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp import models, fields, api, _

class accommodation_analysis(models.Model):
    _name = "accommodation.analysis.report"
    _description = "Accommodation Analysis"
    _auto = False
    
    sr_no=fields.Char('Sr.No')
    paying_comp_id=fields.Many2one('res.company','COM')
    accommodation_id = fields.Many2one('accommodation.accommodation', 'Accommodation')
    address_id=fields.Many2one('res.partner','Location Address')
    nationality_id=fields.Many2one('res.country', 'Nationality')
    maximum_capacity= fields.Integer('Maximum Capacity')
#     contact_address = fields.Char('Location Address', store=True, related="address_id.contact_address")
#     stay_capacity=fields.Integer('Stay Capacity')
    company_id = fields.Many2one('res.company', 'Company')
    number_of_employee = fields.Integer('Stay Men')
    vacant=fields.Integer('Vacancies')
                
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'accommodation_analysis_report')
        cr.execute("""
            create or replace view accommodation_analysis_report as (
            SELECT
                 min(public.beds_beds.id) as id,
                 accommodation_accommodation.id as accommodation_id,
                 accommodation_accommodation.address_id as address_id, 
                 resource_resource.company_id as company_id, 
                 visa_quota.nationality_id as nationality_id, 
                 accommodation_accommodation.maximum_capacity as maximum_capacity, 
                 accommodation_accommodation.paying_comp_id as paying_comp_id,
                 count(beds_beds.employee_id) as number_of_employee,
                 accommodation_accommodation.maximum_capacity-count(beds_beds.employee_id) as vacant
               FROM 
                 public.accommodation_accommodation, 
                 public.beds_beds, 
                 public.visa_quota, 
                 public.room_room, 
                 public.hr_employee, 
                 public.resource_resource
               WHERE 
                 beds_beds.room_id = room_room.id AND
                 visa_quota.accommodation_id = accommodation_accommodation.id AND
                 room_room.accommodation_id = accommodation_accommodation.id AND
                 hr_employee.emp_country_id = visa_quota.nationality_id AND
                 hr_employee.id = beds_beds.employee_id AND
                 hr_employee.resource_id = resource_resource.id
               GROUP BY
                 visa_quota.nationality_id, 
                 accommodation_accommodation.id, 
                 resource_resource.company_id
            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
