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
        purchase_lines_list = {}
        # get purchase line and calculate qty
        po_model_list = self.env['purchase.order'].search([('project_no', '=', self[0].parent_id.project_no.id),'|',('state', '=', 'approved'), ('state', '=', 'done')])
        for po in po_model_list:
            for line in po.order_line:
                if str(line.product_id.id) in purchase_lines_list:
                    purchase_lines_list[str(line.product_id.id)] += line.product_qty
                else:
                    purchase_lines_list[str(line.product_id.id)] = line.product_qty
        
        for record in self:
            if str(record.product_id.id) in purchase_lines_list:
                record.purchased_qty = purchase_lines_list[str(record.product_id.id)]
            else:
                record.purchased_qty = 0.0
        
    def compute_received_qty(self):
        move_line_list = {}
        # use query get stock_pciking
        query = """
        SELECT picking_id FROM stock_picking p, stock_move m, purchase_order_line pol, purchase_order po
            WHERE po.id in %s and po.id = pol.order_id and pol.id = m.purchase_line_id and m.picking_id = p.id
            GROUP BY picking_id, po.id
        """
        po_model_list = self.env['purchase.order'].search([('project_no', '=', self[0].parent_id.project_no.id),'|',('state', '=', 'approved'), ('state', '=', 'done')])
        
        self.env.cr.execute(query, (tuple([x.id for x in po_model_list]), ))
        picks = self.env.cr.fetchall()
        
        a = ()
        for pick in picks:
            a += pick
        
        for pick_obj in self.env['stock.picking'].browse(a):
            for move in pick_obj.move_lines:
                if move.state == 'done':
                    if str(move.product_id.id) in move_line_list:
                        move_line_list[str(move.product_id.id)] += move.product_qty
                    else:
                        move_line_list[str(move.product_id.id)] = move.product_qty
        
        for record in self:
            if str(record.product_id.id) in move_line_list:
                record.received_qty = move_line_list[str(record.product_id.id)]
            else:
                record.received_qty = 0.0    