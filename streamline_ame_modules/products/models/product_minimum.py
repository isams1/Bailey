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
import openerp
from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_minimum(osv.Model):
    _name = 'product.minimum'

    def _get_product(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = False
            if rec.product_tmp_id:
                product_ids = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', rec.product_tmp_id.id)])
                if product_ids:
                    result[rec.id] = product_ids[0]
        return result

    _columns={
        'location_id': fields.many2one('stock.location', 'Location', required=True, domain=[('usage', '=', 'internal')]),
        'product_tmp_id': fields.many2one('product.template', 'Product'),
        'product_id': fields.function(_get_product, type='many2one', relation='product.product', string='Product'),
        'quantity': fields.float('Minimum Qty'),
    }
