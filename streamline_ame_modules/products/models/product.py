# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import SUPERUSER_ID

class product_product(osv.osv):
    _inherit = "product.product"
    
    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'Product Code must be unique!'),
    ]
    
    def init(self, cr):
        cr.execute("""
            select id
            from product_product
            where id in
            (
            select id
            from product_product
            where default_code is NULL
            UNION
            select MAX(id)
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
            )
            order by 1
        """)
        products = self.browse(cr, SUPERUSER_ID, [r[0] for r in cr.fetchall()])
        for product in products:
            vals = {}
            if product.default_code:
                vals['default_code'] = product.default_code + str(product.id)
            else:
                vals['default_code'] = str(product.id)
            self.write(cr, SUPERUSER_ID, product.id, vals)
        
product_product()