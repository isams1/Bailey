# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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

class hr_contract(osv.Model):

    _inherit = 'hr.contract'

    _columns = {
        'wage_to_pay': fields.float('Wage To Pay'),
        'rate_per_hour': fields.float('Rate per hour for part timer'),
        'active_employee': fields.related('employee_id', 'active', type="boolean", string="Active Employee"),
    }

    def _check_date(self, cr, uid, ids, context=None):
        for contract in self.browse(cr, uid, ids,context=context):
            domain = [
                ('date_start', '<=', contract.date_end),
                ('date_end', '>=', contract.date_start),
                ('employee_id', '=', contract.employee_id.id),
                ('id', '!=', contract.id),
            ]
            contract_ids=self.search(cr,uid,domain,context=context,count=True)
            if contract_ids:
                return False
        return True

    _constraints = [
        (_check_date, 'You can not have 2 contract that overlaps on same date!', ['date_end','date_start']),
    ]

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        result = {'value': {}}
        if employee_id:
            active_employee = self.pool.get('hr.employee').browse(cr, uid, employee_id).active
            result['value'].update({'active_employee': active_employee})
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
