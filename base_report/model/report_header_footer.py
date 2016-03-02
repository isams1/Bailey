# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

class ir_actions_report_xml_header_footer(models.Model):
    _name = "ir.actions.report.xml.header.footer"

    header_img = fields.Binary("Header", help="This field holds the image used as Report Header")
    footer_img = fields.Binary("Footer", help="This field holds the image used as Report Footer")
    company_id = fields.Many2one('res.company', 'Company')
    action_report_id = fields.Many2one('ir.actions.report.xml', 'Action Report')

