from openerp import models, fields
import time

class streamline_ame_material_take_off(models.Model):
    _name = "streamline.ame.material.take.off"
    
    name = fields.Char(string='Name', size=256, select=True, default='/')
    project_no = fields.Many2one('streamline.ame.project.project', string='Project Name')
    start_date = fields.Date(string='Report Start Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date = fields.Date(string='Report End Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('streamline.ame.material.take.off.line', 'parent_id')
    
class streamline_ame_material_take_off_line(models.Model):
    _name = "streamline.ame.material.take.off.line"
    
    name = fields.Char(string='Name', size=256, select=True, default='/')
    product_id = fields.Many2one('product.product', required=True, string="Items")
    parent_id = fields.Many2one('streamline.ame.material.take.off', required=True)
    required_qty = fields.Integer(string="Required Qty")
    purchased_qty = fields.Float(compute='compute_purchased_qty', string="Total Purchased Qty")
    received_qty = fields.Float(compute='compute_received_qty', string="Total Received Qty")

    def compute_purchased_qty(self):
        for record in self:
            record.purchased_qty = 0.0
        
    def compute_received_qty(self):
        for record in self:
            record.received_qty = 0.0    