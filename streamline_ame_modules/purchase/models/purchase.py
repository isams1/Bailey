from openerp import models, fields

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    project_no = fields.Char(string='Project', size=256, select=True, default='/')