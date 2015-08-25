# -*- coding: utf-8 -*-
from openerp import models

def update_res_partner_is_company(cr):    
    cr.execute("UPDATE res_partner "
               "SET is_company = 't' "
               "WHERE is_company = 'f' ")

class res_partner(models.Model):
    _inherit = "res.partner"
    
    _defaults = {
        'is_company': True
    }
    
    def init(self, cr):
        cr.execute("UPDATE res_partner "
               "SET is_company = 't' "
               "WHERE is_company = 'f' ")