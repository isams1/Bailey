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
from openerp.addons.streamline_ame_modules.reports.streamline import int_format
_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.streamline.ame.material.take.off.xls'

WANTED_LIST = ['A', 'B', 'C', 'D']

TEMPLATE_CHANGES = {}

class report_streamline_ame_material_take_off_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_streamline_ame_material_take_off_xls_parser, self).__init__(
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
            'get_material_data': self._get_material_data
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src
            
    def get_data(self, obj):
        data = {}
        env = Environment(self.cr, self.uid, self.context)
        user = env['res.users']
        recs = user.search([('id', '=', self.context['uid'])])[0]
        data['company'] = recs.company_id.name
        #material_obj = env['streamline.ame.material.take.off'].browse(self.context['active_id'])
        data['start_date'] = obj.start_date
        data['end_date'] = obj.end_date
        data['project_name'] = obj.project_no.name
        return data
    
    def get_data_wizard(self, obj):
        data = self.get_data(obj)
        return data
    
    def _get_material_data(self, obj):
        env = Environment(self.cr, self.uid, self.context)
        env.invalidate_all()
        material_obj = env['streamline.ame.material.take.off'].browse(obj.id)        
        res = material_obj.line_ids
        return res


class report_streamline_ame_material_take_off_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(report_streamline_ame_material_take_off_xls, self).__init__(
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
        self.aml_cell_style_int = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=int_format)
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
                'header': [1, 20, 'text', _render("_('Item')")],
                'lines': [1, 0, 'text', _render("line.product_id.name")],
                'totals': [1, 0, 'text', None]},
            'B': {
                'header': [1, 13, 'text', _render("_('Required qty')")],
                'lines': [1, 0, 'number', _render("line.required_qty"), None, self.aml_cell_style_int],
                'totals': [1, 0, 'text', None]},
            'C': {
                'header': [1, 18, 'text', _render("_('Purchased qty')")],
                 'lines': [1, 0, 'number', _render("line.purchased_qty"), None, self.aml_cell_style_int],
                'totals': [1, 0, 'text', None]},
            'D': {
                'header': [1, 18, 'text', _render("_('Received qty')")],
                 'lines': [1, 0, 'number', _render("line.received_qty"), None, self.aml_cell_style_int],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._
        
        for obj in objects:
            r_data = _p.get_data_wizard(obj)
    
            # report_name = objects[0]._description or objects[0]._name
            report_name = _("Material Take Off Report")
            ws = wb.add_sheet(r_data['project_name'] or u"No Name")
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
            
            # Title 2
            cell_style = xlwt.easyxf(streamline_xls_styles['xls_sub_title'])
            c_specs = [
                ('project_str', 1, 0, 'text', 'Project name:'),
                ('project_name', 1, 0, 'text', r_data['project_name']),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
            
            # Title 3
            cell_style = xlwt.easyxf(streamline_xls_styles['xls_sub_title'])
            c_specs = [
                ('start_date_str', 1, 0, 'text', 'Report start date:'),
                ('start_date_name', 1, 0, 'text', datetime.strptime(r_data['start_date'], '%Y-%m-%d').strftime('%d-%m-%Y')),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
            
            # Title 3
            cell_style = xlwt.easyxf(streamline_xls_styles['xls_sub_title'])
            c_specs = [
                ('end_date_str', 1, 0, 'text', 'Report end date:'),
                ('end_date_name', 1, 0, 'text', datetime.strptime(r_data['end_date'], '%Y-%m-%d').strftime('%d-%m-%Y')),
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
            
            objects_line = _p.get_material_data(obj)
            
            # lines
            for line in objects_line:
                c_specs = map(
                    lambda x: self.render(x, self.col_specs_template, 'lines'),
                    wanted_list)
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(
                    ws, row_pos, row_data, row_style=self.aml_cell_style)

report_streamline_ame_material_take_off_xls('report.report_streamline_ame_material_take_off_xls',
              'streamline.ame.material.take.off',
              parser=report_streamline_ame_material_take_off_xls_parser)