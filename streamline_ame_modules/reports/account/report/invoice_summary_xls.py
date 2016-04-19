# -*- encoding: utf-8 -*-

import xlwt
from datetime import datetime
import time
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
from openerp.api import Environment
from openerp.addons.streamline_ame_modules.reports.streamline import streamline_xls_styles
_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.streamline.ame.invoice.summary.xls'

WANTED_LIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']

TEMPLATE_CHANGES = {}

class report_streamline_ame_invoice_summary_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_streamline_ame_invoice_summary_xls_parser, self).__init__(
            cr, uid, name, context=context)
        self.context = context
        wanted_list = WANTED_LIST
        template_changes = TEMPLATE_CHANGES
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
            'get_data_wizard': self.get_data_wizard,
            'get_invoice_summary': self._get_invoice_summary
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src
            
    def get_data(self):
        data = self.context['data']['form']
        env = Environment(self.cr, self.uid, self.context)
        user = env['res.users']
        recs = user.search([('id', '=', self.context['uid'])])[0]
        data['company'] = recs.company_id.name
        return data
    
    def get_data_wizard(self):
        data = self.get_data()
        return data
    
    def _get_invoice_summary(self):
        form = self.context['data']['form']
        a = form['date_start']
        b = form['date_end']
        
        self.cr.execute('''
        SELECT to_char(ai.date_invoice, 'dd/MM/yyyy') inv_date,
            ai."number" inv_no,
            pp.default_code stock_code,
            pt.name item_name,
            pt.description item_decs,
                substring(sl.complete_name FROM (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_stock,
                rp.name co_name,
                  substring((
                        SELECT string_agg(sp.name, ', ')
                    FROM sale_order so
                    INNER JOIN  sale_order_line sol on so.id = sol.order_id
                    INNER JOIN  procurement_group pg on so.procurement_group_id = pg.id
                    INNER JOIN  stock_picking sp on pg.id = sp.group_id
                    WHERE sol.product_id = ail.product_id
                    ), 2, 1000) do_name,
                 po.name po_name,
                 SUM(ail.price_unit) unit_price,
                 SUM(ail.quantity) qty,
                 SUM(ail.price_subtotal) as amount,
                 SUM(0.07 * ail.price_subtotal) as gst,
                 SUM(ail.price_subtotal + 0.07 * ail.price_subtotal) as total, project.name
                FROM account_invoice_line ail
                INNER JOIN  account_invoice ai on ai.id = ail.invoice_id
                INNER JOIN  product_product pp on ail.product_id = pp.id
                INNER JOIN  product_template pt on pp.product_tmpl_id = pt.id
                INNER JOIN  purchase_invoice_rel pir on pir.invoice_id = ai.id
                INNER JOIN  purchase_order po on pir.purchase_id = po.id
                INNER JOIN  purchase_order_line pol on po.id = pol.order_id and pol.product_id = ail.product_id
                INNER JOIN  stock_move sm on sm.purchase_line_id = pol.id and ail.product_id = sm.product_id
                INNER JOIN  stock_location sl on sl.id = sm.location_dest_id
                INNER JOIN  res_partner rp on po.partner_id = rp.id
                LEFT JOIN streamline_ame_project_project project on po.project_no = project.id
                WHERE ai.type='in_invoice'
                and ai.state='paid'
                and ai.date_invoice::DATE BETWEEN %s::DATE and %s::DATE
            GROUP BY ai.date_invoice, ai."number", pp.default_code, pt.name, pt.description, sl.complete_name, rp.name, ail.product_id, po.name, project.name
                order by project.name, inv_no desc
        ''',(a, b))
        res = self.cr.dictfetchall()
        return res


class report_streamline_ame_invoice_summary_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(report_streamline_ame_invoice_summary_xls, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {
            'A': {
                'header': [1, 20, 'text', _render("_('Inv Date')")],
                'lines': [1, 0, 'text', _render("line.get('inv_date', '')")],
                'totals': [1, 0, 'text', None]},
            'B': {
                'header': [1, 42, 'text', _render("_('Inv No')")],
                'lines': [1, 0, 'text', _render("line.get('inv_no', '')")],
                'totals': [1, 0, 'text', None]},
            'C': {
                'header': [1, 42, 'text', _render("_('Stock Code')")],
                'lines': [1, 0, 'text', _render("line.get('stock_code', '')")],
                'totals': [1, 0, 'text', None]},
            'D': {
                'header': [1, 13, 'text', _render("_('Item Description')")],
                'lines': [1, 0, 'text', _render("line.get('item_decs') and line.get('item_decs') or line.get('item_name')")],
                'totals': [1, 0, 'text', None]},
            'E': {
                'header': [1, 12, 'text', _render("_('Location')")],
                'lines': [1, 0, 'text', _render("line.get('location_stock', '')")],
                'totals': [1, 0, 'text', None]},
            'F': {
                'header': [1, 36, 'text', _render("_('CO Name')")],
                'lines': [1, 0, 'text', _render("line.get('co_name', '')")],
                'totals': [1, 0, 'text', None]},
            'G': {
                'header': [1, 36, 'text', _render("_('DO Name')")],
                'lines': [1, 0, 'text', _render("line.get('do_name', '')")],
                'totals': [1, 0, 'text', None]},
            'H': {
                'header': [1, 12, 'text', _render("_('PO No')")],
                'lines': [1, 0, 'text', _render("line.get('po_name', '')")],
                'totals': [1, 0, 'text', None]},
            'I': {
                'header': [1, 13, 'text', _render("_('Unit Price')")],
                'lines': [1, 0, 'number', _render("line.get('unit_price', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'J': {
                'header': [1, 18, 'text', _render("_('Balance qty')")],
                 'lines': [1, 0, 'number', _render("line.get('qty', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'K': {
                'header': [1, 18, 'text', _render("_('Amount')")],
                 'lines': [1, 0, 'number', _render("line.get('amount', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'L': {
                'header': [1, 18, 'text', _render("_('GST')")],
                  'lines': [1, 0, 'number', _render("line.get('gst', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'M': {
                'header': [1, 12, 'text', _render("_('Total Amount')")],
                   'lines': [1, 0, 'number', _render("line.get('total', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._
        
        r_data = _p.get_data_wizard()

        # report_name = objects[0]._description or objects[0]._name
        report_name = _("Invoice Summary")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title 1
        cell_style = xlwt.easyxf(streamline_xls_styles['xls_title'])
        c_specs = [('report_name', 2, 0, 'text', report_name)]
        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des1', 1, 0, 'text', 'Report description')]
        row_data = self.xls_row_template(c_specs, ['des1'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des2', 1, 0, 'text', 'Shows summary of paid supplier invoices')]
        row_data = self.xls_row_template(c_specs, ['des2'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des3', 1, 0, 'text', 'Date selection uses supplier invoice date')]
        row_data = self.xls_row_template(c_specs, ['des3'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des4', 1, 0, 'text', 'Unit price comes from purchase order data')]
        row_data = self.xls_row_template(c_specs, ['des4'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        row_pos += 1
        
        # Title 2
        cell_style = xlwt.easyxf(streamline_xls_styles['xls_sub_title'])
        c_specs = [
            ('company', 1, 0, 'text', 'Company:'),
            ('printdate', 1, 0, 'text', 'Print Date:'),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [
            ('company_str', 1, 0, 'text', r_data['company']),
            ('printdate_str', 1, 0, 'text', time.strftime("%d-%m-%Y")),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf(streamline_xls_styles['xls_sub_title'])
        c_specs = [
            ('startperiod', 1, 0, 'text', 'Start Period:'),
            ('endperiod', 1, 0, 'text', 'End Period:'),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [
            ('startperiod_str', 1, 0, 'text', datetime.strptime(r_data['date_start'], '%Y-%m-%d').strftime('%d-%m-%Y')),
            ('endperiod_str', 1, 0, 'text', datetime.strptime(r_data['date_end'], '%Y-%m-%d').strftime('%d-%m-%Y')),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        row_pos += 1

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_template, 'header', render_space={'_': _p._}),
            wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)
        
        objects = _p.get_invoice_summary()
        
        # lines
        for line in objects:
            c_specs = map(
                lambda x: self.render(x, self.col_specs_template, 'lines'),
                wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

report_streamline_ame_invoice_summary_xls('report.report_streamline_ame_invoice_summary_xls',
              'account.invoice',
              parser=report_streamline_ame_invoice_summary_xls_parser)