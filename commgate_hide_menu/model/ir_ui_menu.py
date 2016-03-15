from openerp import models, fields

class ir_ui_menu(models.Model):
    _inherit = "ir.ui.menu"
    
    active = fields.Boolean('Active', default=True)