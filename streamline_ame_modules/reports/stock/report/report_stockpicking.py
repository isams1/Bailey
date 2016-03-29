# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Genpex (<http://http://www.genpex.com>).
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
import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class report_stockpicking(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context=None):
        super(report_stockpicking, self).__init__(cr, uid, name, context=context)
        self.index = 0
        self.localcontext.update({
            'time': time,
            'show_date': self._show_date,
        })

    def _display_address(self, cr, uid, address):
        address_format = "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
            'ad_phone': address.phone or '',
            'ac_mobile': address.mobile or '',
        }
        for field in self.pool.get('res.partner')._address_fields(cr, uid):
            args[field] = getattr(address, field) or ''

        if address.phone:
            address_format = address_format + '\n Phone: %(ad_phone)s'
        if address.mobile:
            address_format = address_format + '\n Mobile: %(ac_mobile)s'
        return address_format % args

    def get_address(self, partner):
        return self._display_address(self.cr, self.uid, partner)

    def _show_date(self, date):
        if not date:
            date = datetime.now()
        else:
            date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        date = date.strftime('%d %b %Y')
        return date

class report_stockpicking_action(osv.AbstractModel):
    _name = 'report.stock.report_picking'
    _inherit = 'report.abstract_report'
    _template = 'stock.report_picking'
    _wrapped_report_class = report_stockpicking

report_stockpicking_action()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
