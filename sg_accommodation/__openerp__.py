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
{
    'name': 'Accommodation',
    'version': '1.59',
    'category': 'General',
    'summary': 'SG Accommodation',
    'author' : 'Serpent Consulting Services Pvt.Ltd.',
    'website' : 'http://www.serpentcs.com',
    'depends': ['account', 'report_aeroo'],
    'data': [ 
             'report_view.xml',
             'security/ir.model.access.csv',
             'wizard/wiz_create_room_bed_view.xml',
             'wizard/wiz_allocate_emp_view.xml',
             'wizard/wiz_vacant_bed_view.xml',
             'wizard/add_nationality_view.xml',
             'accommodation_agreement_view.xml',
             'wizard/wiz_emp_away_history.xml',
             'report/accommodation_anyalysis_report_view.xml',
             'views/tenancy_agreement_report.xml',
             'wizard/wiz_accommodation_report_view.xml',
             'wizard/wiz_accommodation_nationality_report_view.xml',
             'views/report_location_view.xml',
             'views/nationality_accommodation_view.xml',
             'wizard/wiz_new_emp_acc_report_view.xml',
             'wizard/wiz_resigned_emp_acc_report_view.xml',
             'wizard/wiz_accommodation_report_date_view.xml',
             'wizard/wiz_accommodation_employee_report_view.xml',
             'wizard/wiz_pub_history_view.xml',
             'views/site_view.xml'
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
