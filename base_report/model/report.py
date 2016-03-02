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

class ir_actions_report_xml(models.Model):
    _inherit = "ir.actions.report.xml"

    header_footer_ids = fields.One2many('ir.actions.report.xml.header.footer', 'action_report_id', 'Header Footer IMG')

    def get_header(self, company_id):
        header = False
        for report in self:
            for line in report.header_footer_ids:
                if line.company_id and line.company_id.id == company_id:
                    header = line.header_img
                    break
                if not line.company_id:
                    header = line.header_img
        return header

    def get_footer(self, company_id):
        footer = False
        for report in self:
            for line in report.header_footer_ids:
                if line.company_id and line.company_id.id == company_id:
                    footer = line.footer_img
                    break
                if not line.company_id:
                    footer = line.footer_img
        return footer

class Report(models.Model):
    _inherit = "report"
    _description = "Report"

    #--------------------------------------------------------------------------
    # Main report methods
    #--------------------------------------------------------------------------
    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        """This method generates and returns html version of a report.
        """
        # If the report is using a custom model to render its html, we must use it.
        # Otherwise, fallback on the generic html rendering.
        try:
            report_model_name = 'report.%s' % report_name
            particularreport_obj = self.pool[report_model_name]
            report = self._get_report_from_name(cr, uid, report_name)
            if context == None:
                context ={}
            context.update({'report': report,})
            return particularreport_obj.render_html(cr, uid, ids, data=data, context=context)
        except KeyError:
            report = self._get_report_from_name(cr, uid, report_name)
            report_obj = self.pool[report.model]
            docs = report_obj.browse(cr, uid, ids, context=context)
            docargs = {
                'doc_ids': ids,
                'doc_model': report.model,
                'docs': docs,
                'report': report,
            }
            return self.render(cr, uid, [], report.report_name, docargs, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
