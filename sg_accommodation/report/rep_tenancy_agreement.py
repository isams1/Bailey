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

from openerp.report import report_sxw
from openerp.osv import osv
import time 
from datetime import datetime
from openerp.tools import amount_to_text_en

class report_rep_tenancy_agreement(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.counter = 0
        super(report_rep_tenancy_agreement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'get_rooms' : self.get_rooms,
              'get_rate': self.get_rate,
              'get_date' : self.get_date,
              'get_partner' : self.get_partner,
              'get_date_format' : self.get_date_format,
        })
        
    def get_partner(self, address_id):
        if address_id.parent_id:
            return address_id.parent_id.name
        else:
            return address_id.name
    
    def get_rooms(self, maximum , stay):
        diff = maximum - stay
        return diff
        
    def get_rate(self, rent, maximum , stay):
        diff = maximum - stay
        cal_rate = rent * diff
        return cal_rate
    
    def get_date(self):
        return time.strftime('%d %B %Y')
    
    def get_date_format(self, date_start):
        if date_start:
            time_val = datetime.strptime(date_start, '%Y-%m-%d') 
            time_for = datetime.strftime(time_val, '%d %B %Y') 
            return time_for
        return ''
        
# class report_test(osv.AbstractModel):
#    _name = "report.accommodation.rep_acco_tenancy_agreement"
#    _inherit = "report.abstract_report"
#    _template = "accommodation.rep_acco_tenancy_agreement"
#    _wrapped_report_class = report_rep_tenancy_agreement
#    
    
class report_test(osv.AbstractModel):
    _name = "report.accommodation.tenancy_agreement_report"
    _inherit = "report.abstract_report"
    _template = "accommodation.tenancy_agreement_report"
    _wrapped_report_class = report_rep_tenancy_agreement
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
