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

class tenancy_agreement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        self.counter = 0
        super(tenancy_agreement_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'get_rooms_ids' : self.get_rooms_ids,
              'get_total' : self.get_total,
              'get_rate': self.get_rate,
              'get_corr_add' : self.get_corr_add,
        })
        
        
    def get_corr_add(self, corr_address):
        if corr_address:
            address = corr_address.contact_address
            return address
        
    def get_partner(self, address_id):
        if address_id.parent_id:
            return address_id.parent_id.name
        else:
            return address_id.name
    
    def get_total(self, occupied, total_amount, service, furniture, charges):
        serv_total = (service * 7.0) / 100
        furn_total = (furniture * 7.0) / 100
        charges_total = (charges * 7.0) / 100
        total = occupied * (total_amount + serv_total + furn_total + charges_total)
        return total
        
    def get_rate(self, occupied, total_amount):
        total_deposit = 2 * (occupied * total_amount)
        return total_deposit
    
    def get_rooms_ids(self, room_ids):
        room = ''
        if room_ids:
            for rooms in room_ids:
                room += '#' + rooms.name + ',' 
        return room[:-1]
        
    
class report_test(osv.AbstractModel):
    _name = "report.accommodation.tenancy_agreement_report"
    _inherit = "report.abstract_report"
    _template = "accommodation.tenancy_agreement_report"
    _wrapped_report_class = tenancy_agreement_report
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
