# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.report import report_sxw
from openerp.osv import osv

class nationality_accommodation(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(nationality_accommodation, self).__init__(cr, uid, name, context=context)
        self.counter = 0
        self.localcontext.update({'get_companies':self.get_companies,
        })
        self.context = context
        
    def get_companies(self):
        company_list=[]
        self.td_list = []
        comp_obj = self.pool.get('res.company')
        comp_ids=comp_obj.search(self.cr,self.uid,[('tenant', '=', True)])
        for comp in comp_obj.browse(self.cr,self.uid,comp_ids):
            company_list.append(comp.code)
            if company_list:
                company_list.sort()
            no_of_td=company_list
            for td in range(0,len(no_of_td)):
                self.td_list.append(td)
        return company_list
    
class report_nationality_accommodation(osv.AbstractModel):
    _name = 'report.accommodation.view_nationality_report'
    _inherit = 'report.abstract_report'
    _template = 'accommodation.view_nationality_report'
    _wrapped_report_class = nationality_accommodation
