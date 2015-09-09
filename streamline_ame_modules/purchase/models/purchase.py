from openerp import models, fields

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    project_no = fields.Many2one('streamline.ame.project.project')