# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

def update_null_and_slash_codes(cr):
    """
    Updates existing codes matching the default '/' or
    empty. Primarily this ensures installation does not
    fail for demo data.
    :param cr: database cursor
    :return: void
    """
    cr.execute("UPDATE product_product "
               "SET default_code = 'PR' || id "
               "WHERE default_code IS NULL OR default_code = '/';")
    
    cr.execute("""
            update product_product
            set default_code = default_code || id
            where id in
            (
            select pp.id
            from product_product pp INNER JOIN 
            (
            select default_code, MAX(id) id
            from product_product
            where default_code in 
            (
            select default_code
            from product_product
            where default_code is not NULL
            group by default_code
            having count(1) > 1
            order by default_code
            )
            group by default_code
            order by 1
            ) tmp_pp on pp.default_code = tmp_pp.default_code and pp.id < tmp_pp.id
            order by 1
            )
        """)   

class product_product(models.Model):
    _inherit = "product.product"

    templ_minimum_ids = fields.One2many('product.minimum', 'product_id', string='Minimum Qty')
    default_code = fields.Char(
        string='Reference',
        size=64,
        select=True,
        required=True,
        default='/')
    
    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'Product Code must be unique!'),
    ]  
    
    @api.model
    def create(self, vals):
        if 'default_code' not in vals or vals['default_code'] == '/':
            vals['default_code'] = self.env['ir.sequence'].get(
                'product.product')
        return super(product_product, self).create(vals)

    @api.multi
    def write(self, vals):
        for product in self:
            if product.default_code in [False, '/']:
                vals['default_code'] = self.env['ir.sequence'].get(
                    'product.product')
            super(product_product, product).write(vals)
        return True

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.default_code:
            default.update({
                'default_code': self.default_code + _('-copy'),
            })

        return super(product_product, self).copy(default)

    def check_inventory(self, cr, uid, product_ids, location_id, context=None):
        product_inventory = self._product_available(cr, uid,
                product_ids,
                context={'location': location_id})
        warning = {}
        for product in self.browse(cr, uid, product_ids, context):
            for minimum in product.product_tmpl_id.templ_minimum_ids:
                if minimum.location_id and minimum.location_id.id == location_id:
                    if product_inventory[product.id]['qty_available'] > minimum.quantity:
                        warning.update({product.id: minimum.quantity})
        return warning
        
product_product()

class product_template(models.Model):
    _inherit = "product.template"
    
    templ_minimum_ids = fields.One2many('product.minimum', 'product_tmp_id', string='Minimum Qty')
    living_material_price = fields.Float('Living-Material', digits_compute=dp.get_precision('Product Price'))
    living_labour_price = fields.Float('Living-Labour', digits_compute=dp.get_precision('Product Price'))
    machinery_material_price = fields.Float('Machinery-Material', digits_compute=dp.get_precision('Product Price'))
    machinery_labour_price = fields.Float('Machinery-Labour', digits_compute=dp.get_precision('Product Price'))
    living_material_by_ame = fields.Boolean('By AME')
    living_labour_by_ame = fields.Boolean('By AME')
    machinery_material_by_ame = fields.Boolean('By AME')
    machinery_labour_by_ame = fields.Boolean('By AME')
product_template()    