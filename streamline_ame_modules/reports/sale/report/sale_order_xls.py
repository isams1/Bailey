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

import openerp
from openerp import pooler
from openerp.report import report_sxw
import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from openerp.tools.translate import _


class sale_order_xls_parser(report_sxw.rml_parse):
    def __init__(self, cursor, uid, name, context):
        super(sale_order_xls_parser, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('SALE ORDER'),
            'get_header_img': self._get_header_img,
            'get_address': self.get_address,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-spacing', '2'),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_header_img(self):
        objects = self.objects
        cr, uid = self.cr, self.uid
        report_obj = self.pool['ir.actions.report.xml']
        conditions = [('report_type', '=', 'xls'), ('report_name', '=', self.name)]
        idreport = report_obj.search(cr, uid, conditions)[0]
        report = report_obj.browse(cr, uid, idreport)
        return report.get_header(objects[0].company_id.id)

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


_column_sizes = [
    ('0', 20),
    ('1', 20),
    ('2', 10),
    ('3', 10),
    ('4', 10),
    ('5', 10),
    ('6', 10),
    ('7', 10),
    ('8', 20),
]
import time


class sale_order_xls(report_xls):
    column_sizes = [x[1] for x in _column_sizes]

    def resize_image(self, path):
        import PIL
        from PIL import Image

        basewidth = 100
        img = Image.open(path)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        img.save(path)

        return

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 6

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # add img
        from PIL import Image
        header_img = _p.get_header_img()
        # insert pic header
        image_path = openerp.modules.get_module_resource('streamline_ame_modules', 'reports/sale/report')

        fh = open(image_path + "/banner.png", "wb")
        fh.write(header_img.decode('base64'))
        fh.close()

        img = Image.open(image_path + "/banner.png")
        r, g, b, a = img.split()
        img = Image.merge("RGB", (r, g, b))
        img.save(image_path + "/imagetoadd.bmp")

        ws.insert_bitmap(image_path + "/imagetoadd.bmp", 0, 1, scale_x=0.5, scale_y=0.6)

        # write empty row to define column sizes
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)

        cell_format = _xs['bold'] + _xs['underline']
        so_style = xlwt.easyxf(cell_format)

        cell_format = _xs['bold'] + _xs['borders_all'] + _xs['center']
        table_title_style = xlwt.easyxf(cell_format)

        cell_format = _xs['right']
        right_style = xlwt.easyxf(cell_format)

        cell_format = _xs['underline'] + _xs['right']
        underline_style = xlwt.easyxf(cell_format)

        for so in objects:
            c_specs = [
                ('name', 9, 0, 'text', 'Our Ref: %s' %(so.client_order_ref and so.client_order_ref or '')),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)
            ws.set_horz_split_pos(row_pos)

            c_specs = [
                ('name', 9, 0, 'text', 'Date: %s' % time.strftime('%Y-%m-%d')),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                ('name', 9, 0, 'text', so.partner_invoice_id.name),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                ('name', 9, 0, 'text', _p.get_address(so.partner_invoice_id)),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                (
                'name', 9, 0, 'text', 'Dear Sir %s' % (so.origin and '%s - %s' % (so.name, so.origin) or so.name), None,
                so_style),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                ('name', 9, 0, 'text',
                 'To provide supervision, labour, engineering, materials, and tools to supply and install the followings:'),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            row_pos += 1

            c_specs = [
                ('name', 2, 0, 'text', ''),
                ('living', 3, 0, 'text', 'Living Quarters', None, table_title_style),
                ('machine', 3, 0, 'text', 'Machinery Area', None, table_title_style),
                ('total', 1, 0, 'text', 'Total Amount', None, table_title_style),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                ('1', 2, 0, 'text', ''),
                ('2', 1, 0, 'text', 'Material', None, right_style),
                ('3', 1, 0, 'text', 'Labor', None, right_style),
                ('4', 1, 0, 'text', ''),
                ('5', 1, 0, 'text', 'Material', None, right_style),
                ('6', 1, 0, 'text', 'Labor', None, right_style),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            c_specs = [
                ('1', 2, 0, 'text', '1) Scope of Supply/ Work', None, xlwt.easyxf(_xs['underline'])),
                ('2', 1, 0, 'text', 'By AME', None, underline_style),
                ('3', 1, 0, 'text', 'By AME', None, underline_style),
                ('4', 1, 0, 'text', 'Amount', None, underline_style),
                ('5', 1, 0, 'text', 'By AME', None, underline_style),
                ('6', 1, 0, 'text', 'By AME', None, underline_style),
                ('7', 1, 0, 'text', 'Amount', None, underline_style),
            ]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

            no = 0
            for l in so.order_line:
                no += 1
                c_specs = [
                    ('1', 2, 0, 'text', '1.%s %s' % (no, l.name), None, xlwt.easyxf(_xs['wrap'])),
                    ('2', 1, 0, 'text', l.product_id.living_material_by_ame == True and 'YES' or 'No', None,
                     right_style),
                    ('3', 1, 0, 'text', l.product_id.living_labour_by_ame == True and 'YES' or 'No', None, right_style),
                    ('4', 1, 0, 'text', '', None, right_style),
                    ('5', 1, 0, 'text', l.product_id.machinery_material_by_ame == True and 'YES' or 'No', None,
                     right_style),
                    ('6', 1, 0, 'text', l.product_id.machinery_labour_by_ame == True and 'YES' or 'No', None,
                     right_style),
                    ('7', 1, 0, 'text', '', None, right_style),
                ]
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)

                total = l.product_id.living_material_price + l.product_id.living_labour_price + \
                        l.product_id.machinery_material_price + l.product_id.machinery_labour_price
                c_specs = [
                    ('1', 2, 0, 'text', ''),
                    ('2', 1, 0, 'text', '%s %s' % (so.currency_id.symbol, l.product_id.living_material_price), None,
                     right_style),
                    ('3', 1, 0, 'text', '%s %s' % (so.currency_id.symbol, l.product_id.living_labour_price), None,
                     right_style),
                    ('4', 1, 0, 'text', '%s %s' % (
                    so.currency_id.symbol, l.product_id.living_material_price + l.product_id.living_labour_price), None,
                     right_style),
                    ('5', 1, 0, 'text', '%s %s' % (so.currency_id.symbol, l.product_id.machinery_material_price), None,
                     right_style),
                    ('6', 1, 0, 'text', '%s %s' % (so.currency_id.symbol, l.product_id.machinery_labour_price), None,
                     right_style),
                    ('7', 1, 0, 'text', '%s %s' % (
                    so.currency_id.symbol, l.product_id.machinery_material_price + l.product_id.machinery_labour_price),
                     None, right_style),
                    ('8', 1, 0, 'text', '%s %s' % (so.currency_id.symbol, total), None, right_style),
                ]
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)

                if l.remark:
                    c_specs = [
                        ('1', 2, 0, 'text', ''),
                        ('2', 7, 0, 'text', 'Remarks: %s'%l.remark),
                    ]
                    row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                    row_pos = self.xls_write_row(ws, row_pos, row_data)
            if so.note:
                c_specs = [
                    ('name', 9, 0, 'text', 'Quotation Remarks: %s'%so.note),
                ]
                row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
                row_pos = self.xls_write_row(ws, row_pos, row_data)


sale_order_xls('report.sale.order.list.xls',
               'sale.order',
               parser=sale_order_xls_parser)
