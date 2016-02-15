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

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.result = []
        self.localcontext.update({
#               'get_acc_location_l' : self.get_acc_location_l,
#               'get_lines': self.get_lines,
                'get_total_no_of_vacancy':self.get_total_no_of_vacancy,
              })
        
    def get_total_no_of_vacancy(self, data):
        tot_no_of_vacancy = 0.0
        if data['form']:
            for line in data['form']:
                if line['accomodation'] and line['room'] and line['no_of_vacancy'] != '':
                    tot_no_of_vacancy += line['no_of_vacancy']
        return tot_no_of_vacancy
