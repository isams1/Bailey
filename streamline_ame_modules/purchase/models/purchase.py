from openerp import models, fields, api

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    project_no = fields.Char(string='Project', size=256, select=True, default='/')