# -*- coding: utf-8 -*-

import xlwt
import time
from datetime import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
from openerp.api import Environment
from openerp.addons.streamline_ame_modules.reports.streamline import streamline_xls_styles
_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.streamline.ame.ordered.vs.delivery.qty.xls'

WANTED_LIST = ['A', 'B', 'C', 'D', 'E', 'F']

TEMPLATE_CHANGES = {}

class report_streamline_ame_ordered_vs_delivery_qty_xls_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(report_streamline_ame_ordered_vs_delivery_qty_xls_parser, self).__init__(cr, uid, name, context=context)
        self.context = context
        wanted_list = WANTED_LIST
        template_changes = TEMPLATE_CHANGES
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
            'get_data_wizard': self.get_data_wizard,
            'get_data_summary': self._get_data_summary
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

    def _get_data_summary(self):
        form = self.context['data']['form']
        a = form['date_start']
        b = form['date_end']
        
        self.cr.execute('''
        select pp.name_template prod_code, pt.description prod_description, po.name po_name, pol.product_qty po_qty, sum(sm.product_qty) received_qty,
            substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name 
        from stock_move sm 
        inner join purchase_order_line pol on sm.purchase_line_id = pol.id
        inner join purchase_order po on pol.order_id = po.id
        inner join stock_picking sp on sm.picking_id = sp.id
        inner join product_product pp on sm.product_id = pp.id
        inner join product_template pt on pp.product_tmpl_id = pt.id
        inner join stock_location sl on sm.location_dest_id = sl.id
        where sm.state = 'done'
        and po.date_order::DATE BETWEEN %s::DATE and %s::DATE
        group by 1,2,3,4,6
        order by 3,1
        ''',(a, b))
        res = self.cr.dictfetchall()
        return res

class report_streamline_ame_ordered_vs_delivery_qty_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(report_streamline_ame_ordered_vs_delivery_qty_xls, self).__init__(
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
                'header': [1, 20, 'text', _render("_('Product Code')")],
                'lines': [1, 0, 'text', _render("line.get('prod_code', '')")],
                'totals': [1, 0, 'text', None]},
            'B': {
                'header': [1, 42, 'text', _render("_('Product Description')")],
                'lines': [1, 0, 'text', _render("line.get('prod_description', '')")],
                'totals': [1, 0, 'text', None]},
            'C': {
                'header': [1, 42, 'text', _render("_('Warehouse Location')")],
                'lines': [1, 0, 'text', _render("line.get('location_name', '')")],
                'totals': [1, 0, 'text', None]},
            'D': {
                'header': [1, 13, 'text', _render("_('PO#')")],
                'lines': [1, 0, 'text', _render("line.get('po_name', '')")],
                'totals': [1, 0, 'text', None]},
            'E': {
                'header': [1, 13, 'text', _render("_('PO Qty')")],
                'lines': [1, 0, 'number', _render("line.get('po_qty', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'F': {
                'header': [1, 18, 'text', _render("_('Received Qty')")],
                 'lines': [1, 0, 'number', _render("line.get('received_qty', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._
        
        r_data = _p.get_data_wizard()

        # report_name = objects[0]._description or objects[0]._name
        report_name = _("Ordered Qty Vs Delivery Qty")
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
        c_specs = [('des1', 1, 0, 'text', 'Report description: to measure supplier performance')]
        row_data = self.xls_row_template(c_specs, ['des1'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des2', 1, 0, 'text', 'Selection criteria: PO date')]
        row_data = self.xls_row_template(c_specs, ['des2'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [('des3', 1, 0, 'text', 'Input: PO start date, PO end date')]
        row_data = self.xls_row_template(c_specs, ['des3'])
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
        
        objects = _p.get_data_summary()
        
        # lines
        for line in objects:
            c_specs = map(
                lambda x: self.render(x, self.col_specs_template, 'lines'),
                wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

report_streamline_ame_ordered_vs_delivery_qty_xls('report.report_streamline_ame_ordered_vs_delivery_qty_xls',
              'stock.picking',
              parser=report_streamline_ame_ordered_vs_delivery_qty_xls_parser)
