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

WANTED_LIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

TEMPLATE_CHANGES = {}

class report_streamline_ame_stock_report_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_streamline_ame_stock_report_xls_parser, self).__init__(
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
            'get_stock_report': self._get_stock_report
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
    
    def _get_stock_report(self):
        form = self.context['data']['form']
        a = form['report_month']
        b = form['report_year']
        c = a + '-' + b
        
        self.cr.execute('''
        select case when T.date_invoice is null then null else T.product_name end product_name, case when T.date_invoice is null then 'Subtotal' else T.date_invoice end date_invoice, T.project_no, T.units, T.stock_in, T.stock_out, T.balance, T.unit_price_per_pc, T.amount
        from
        (
        select X.product_name, to_char(X.date_invoice, 'DD-MM-YYYY') date_invoice, X.location_name project_no, X.units,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
                and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s) , 0))) stock_in,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s), 0))) stock_out,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
            and product_qty is not null
            and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0)) as balance),
        COALESCE((select max(value_float)
        from ir_property
        where name = 'standard_price'
        and res_id = 'product.template,' || X.product_template_id), 0) unit_price_per_pc,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
                and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0)) as balance) *
        COALESCE((select max(value_float)
        from ir_property
        where name = 'standard_price'
        and res_id = 'product.template,' || X.product_template_id), 0) amount
        from
        (
        select pu.name units, pt.id product_template_id, pp.id as product_id, pp.name_template as product_name, sl.id as location_id, substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name, max(ai.date_invoice) date_invoice
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join stock_location sl on sl.id = sm.location_id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sl."name" = 'Stock'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        group by 1,2,3,4,5,6
        ) X
        UNION ALL
        select Y.product_name, Y.date_invoice, Y.partner_name, Y.units, Y.stock_in, Y.stock_out, Y.stock_in as balance, Y.unit_price_per_pc, Y.stock_in * Y.unit_price_per_pc amount  
        FROM
        (
        select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
            COALESCE(sum(sm.product_qty), 0) stock_in, 0 stock_out, 
            COALESCE((select max(value_float)
            from ir_property
            where name = 'standard_price'
            and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join purchase_order_line pol on sm.purchase_line_id = pol.id
        inner join purchase_order po on pol.order_id = po.id
        inner join res_partner rp on po.partner_id = rp.id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        and sm.purchase_line_id is not null
        group by 1,2,3,4,5
        ) Y
        union ALL
        select X.product_name, X.date_invoice, X.partner_name, X.units, X.stock_in, X.stock_out, (X.stock_in - X.stock_out) as balance, X.unit_price_per_pc, (X.stock_in - X.stock_out) * X.unit_price_per_pc amount  
        FROM
        (
        select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
            0 stock_in, COALESCE(sum(sm.product_qty), 0) stock_out, 
            COALESCE((select max(value_float)
            from ir_property
            where name = 'standard_price'
            and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join stock_picking sp on sm.picking_id = sp.id
        inner join stock_picking_type spt on spt.id = sp.picking_type_id
        inner join res_partner rp on sp.partner_id = rp.id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        and spt.code = 'outgoing'
        group by 1,2,3,4,5
        ) X
        UNION ALL
        select Z.product_name, null, null, null, sum(Z.stock_in), sum(Z.stock_out), sum(Z.stock_in) - sum(Z.stock_out), max(Z.unit_price_per_pc), (sum(Z.stock_in) - sum(Z.stock_out)) * max(Z.unit_price_per_pc)
        from
        (
        select X.product_name, to_char(X.date_invoice, 'DD-MM-YYYY') date_invoice, X.location_name project_no, X.units,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
                and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s) , 0))) stock_in,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s), 0))) stock_out,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
            and product_qty is not null
            and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0)) as balance),
        COALESCE((select max(value_float)
        from ir_property
        where name = 'standard_price'
        and res_id = 'product.template,' || X.product_template_id), 0) unit_price_per_pc,
        (select (COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_dest_id = X.location_id 
                and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0) - 
            COALESCE((select sum(COALESCE(product_qty,0)) 
                from stock_move 
                where product_id = X.product_id and state in ('done', 'transit') and location_id = X.location_id 
            and product_qty is not null and to_char(date_expected, 'MM-YYYY') = %s group by product_id), 0)) as balance) *
        COALESCE((select max(value_float)
        from ir_property
        where name = 'standard_price'
        and res_id = 'product.template,' || X.product_template_id), 0) amount
        from
        (
        select pu.name units, pt.id product_template_id, pp.id as product_id, pp.name_template as product_name, sl.id as location_id, substring(sl.complete_name from (length('Physical Locations / ') + strpos(sl.complete_name, 'Physical Locations / '))) location_name, max(ai.date_invoice) date_invoice
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join stock_location sl on sl.id = sm.location_id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sl."name" = 'Stock'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        group by 1,2,3,4,5,6
        ) X
        UNION ALL
        select Y.product_name, Y.date_invoice, Y.partner_name, Y.units, Y.stock_in, Y.stock_out, Y.stock_in as balance, Y.unit_price_per_pc, Y.stock_in * Y.unit_price_per_pc amount  
        FROM
        (
        select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
            COALESCE(sum(sm.product_qty), 0) stock_in, 0 stock_out, 
            COALESCE((select max(value_float)
            from ir_property
            where name = 'standard_price'
            and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join purchase_order_line pol on sm.purchase_line_id = pol.id
        inner join purchase_order po on pol.order_id = po.id
        inner join res_partner rp on po.partner_id = rp.id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        and sm.purchase_line_id is not null
        group by 1,2,3,4,5
        ) Y
        union ALL
        select X.product_name, X.date_invoice, X.partner_name, X.units, X.stock_in, X.stock_out, (X.stock_in - X.stock_out) as balance, X.unit_price_per_pc, (X.stock_in - X.stock_out) * X.unit_price_per_pc amount  
        FROM
        (
        select rp.name partner_name, pu.name units, pt.id product_template_id, pp.id product_id, pp.name_template product_name, to_char(max(ai.date_invoice), 'DD-MM-YYYY') as date_invoice, 
            0 stock_in, COALESCE(sum(sm.product_qty), 0) stock_out, 
            COALESCE((select max(value_float)
            from ir_property
            where name = 'standard_price'
            and res_id = 'product.template,' || pt.id), 0) unit_price_per_pc
        from account_invoice ai
        inner join account_invoice_line ail on ai.id = ail.invoice_id
        INNER JOIN product_product pp on ail.product_id = pp.id
        INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        inner join product_uom pu on pt.uom_id = pu.id
        inner join stock_move sm on ail.product_id = sm.product_id
        inner join stock_picking sp on sm.picking_id = sp.id
        inner join stock_picking_type spt on spt.id = sp.picking_type_id
        inner join res_partner rp on sp.partner_id = rp.id
        where ai.type='in_invoice'
        and ai.state='paid'
        and sm."state" in ('transit', 'done')
        and to_char(ai.date_invoice, 'MM-YYYY') = %s
        and to_char(sm.date_expected, 'MM-YYYY') = %s
        and spt.code = 'outgoing'
        group by 1,2,3,4,5
        ) X
        order by 1,2
        ) Z
        GROUP BY product_name
        order by 1,2
        ) T
        ''',(c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c,c))
        res = self.cr.dictfetchall()
        return res


class report_streamline_ame_stock_report_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(report_streamline_ame_stock_report_xls, self).__init__(
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
                'header': [1, 20, 'text', _render("_('Product')")],
                'lines': [1, 0, 'text', _render("line.get('product_name', '')")],
                'totals': [1, 0, 'text', None]},
            'B': {
                'header': [1, 42, 'text', _render("_('Date')")],
                'lines': [1, 0, 'text', _render("line.get('date_invoice', '')")],
                'totals': [1, 0, 'text', None]},
            'C': {
                'header': [1, 13, 'text', _render("_('Stock In')")],
                'lines': [1, 0, 'number', _render("line.get('stock_in', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'D': {
                'header': [1, 13, 'text', _render("_('Stock Out')")],
                'lines': [1, 0, 'number', _render("line.get('stock_out', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'E': {
                'header': [1, 12, 'text', _render("_('Project No/ Customer')")],
                'lines': [1, 0, 'text', _render("line.get('project_no', '')")],
                'totals': [1, 0, 'text', None]},
            'F': {
                'header': [1, 13, 'text', _render("_('Balance of Stock')")],
                'lines': [1, 0, 'number', _render("line.get('balance', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'G': {
                'header': [1, 36, 'text', _render("_('Units')")],
                'lines': [1, 0, 'text', _render("line.get('units', '')")],
                'totals': [1, 0, 'text', None]},
            
            'H': {
                'header': [1, 13, 'text', _render("_('Unit')")],
                'lines': [1, 0, 'number', _render("line.get('unit_price_per_pc', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'I': {
                'header': [1, 18, 'text', _render("_('Amount')")],
                 'lines': [1, 0, 'number', _render("line.get('amount', None)"), None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._
        
        r_data = _p.get_data_wizard()

        # report_name = objects[0]._description or objects[0]._name
        report_name = _("Stock Report")
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
        c_specs = [('des2', 1, 0, 'text', 'Shows product with invoice transactions in this month only')]
        row_data = self.xls_row_template(c_specs, ['des2'])
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
            ('month', 1, 0, 'text', 'Month:'),
            ('year', 1, 0, 'text', 'Year:'),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
        
        cell_style = xlwt.easyxf()
        c_specs = [
            ('month_str', 1, 0, 'text', r_data['report_month']),
            ('year_str', 1, 0, 'text', r_data['report_year']),
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
        
        objects = _p.get_stock_report()
        
        # lines
        for line in objects:
            c_specs = map(
                lambda x: self.render(x, self.col_specs_template, 'lines'),
                wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

report_streamline_ame_stock_report_xls('report.report_streamline_ame_stock_report_xls',
              'account.invoice',
              parser=report_streamline_ame_stock_report_xls_parser)