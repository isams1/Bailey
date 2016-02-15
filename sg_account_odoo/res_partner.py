# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Tech Receptives (<http://techreceptives.com>).
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

from openerp.osv import osv, fields

class res_partner(osv.Model):
    
    _inherit = 'res.partner'

    _columns = {
        'customer_uen': fields.char('Customer UEN', size=64),
        'customer_id': fields.char('Customer ID', size=16),
        'supplier_uen': fields.char('Supplier UEN', size=64),
    }
    
    _sql_constraints = [
        ('customer_id_uniq', 'unique(customer_id)', 'Customer ID must be unique per Customer!'),
    ]


class res_company(osv.Model):
    
    _inherit = 'res.company'

    _columns = {
        'company_uen': fields.char('Company UEN', size=64),
        'gst_no': fields.char('GST No', size=64),
        'period_start': fields.date('Period Start'),
        'period_end': fields.date('Period End'),
        'iaf_creation_date': fields.date('IAF Creation Date'),
        'product_version': fields.char('Product Version', size=32),
        'iaf_version': fields.char('IAF Version', size=32),
    }

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    _columns = {
            'permit_no': fields.char('Permit No.', size=32)
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
