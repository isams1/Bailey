# -*- coding: utf-8 -*-
from openerp.addons.web.http import Controller, route, request
from openerp.addons.web.controllers.main import _serialize_exception
from openerp.osv import osv
from openerp.tools import html_escape

import simplejson
from werkzeug import exceptions, url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers
from reportlab.graphics.barcode import createBarcodeDrawing

from openerp.addons.report.controllers.main import ReportController
import openerp
import logging
import time

_logger = logging.getLogger(__name__)

class ReportController(ReportController):
    
    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = simplejson.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        try:
            if type == 'qweb-pdf':
                reportname = url.split('/report/pdf/')[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids, converter='pdf')
                else:
                    # Particular report:
                    data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
                    response = self.report_routes(reportname, converter='pdf', **dict(data))
                    
                cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
                report_obj = request.registry['ir.actions.report.xml']
                idreport = report_obj.search(cr, uid, [('report_name', '=', reportname)], context=context)
                try:
                    report = report_obj.browse(cr, uid, idreport[0], context=context)
                    reportname = report.report_file  + '_' + time.strftime('%Y%m%d', time.gmtime())
                except IndexError:
                    _logger.error("Can not lookup report %s" % reportname)
                
                response.headers.add('Content-Disposition', 'attachment; filename=%s.pdf;' % reportname)
                response.set_cookie('fileToken', token)
                return response
            elif type =='controller':
                reqheaders = Headers(request.httprequest.headers)
                response = Client(request.httprequest.app, BaseResponse).get(url, headers=reqheaders, follow_redirects=True)
                response.set_cookie('fileToken', token)
                return response
            else:
                return
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(simplejson.dumps(error)))