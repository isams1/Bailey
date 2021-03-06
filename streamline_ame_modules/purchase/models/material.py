from openerp import models, fields
import time
from lxml import etree
import simplejson as json
import logging

log = logging.getLogger(__name__)

class streamline_ame_material_take_off(models.Model):
    _name = "streamline.ame.material.take.off"
    
    def check_general_group(self, cr, uid, res_user_id , context = None):
        result = False
        try:
            model_data = self.pool.get('ir.model.data')
            general_id = model_data.xmlid_lookup(cr, uid, "streamline_ame_modules.ame_general")[2]
            user_obj = self.pool.get('res.users').browse(cr, uid, res_user_id, context=context)
            
            for user_group in user_obj.groups_id:
                if user_group.id == general_id:
                    return True
        except Exception as e:
            logging.getLogger.info(e)
        return result

    name = fields.Char(string='Name', size=256, select=True, default='/')
    project_no = fields.Many2one('streamline.ame.project.project', string='Project Name')
    start_date = fields.Date(string='Report Start Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    end_date = fields.Date(string='Report End Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('streamline.ame.material.take.off.line', 'parent_id')
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(streamline_ame_material_take_off, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if self.check_general_group(cr, uid, uid, context):
            doc = etree.XML(res['arch'])
            if view_type == 'form':
                nodes = doc.xpath("//form")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
            if view_type == 'tree':
                nodes = doc.xpath("//tree")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
            res['arch'] = etree.tostring(doc)
        return res
    
class streamline_ame_material_take_off_line(models.Model):
    _name = "streamline.ame.material.take.off.line"
    
    name = fields.Char(string='Name', size=256, select=True, default='/')
    product_id = fields.Many2one('product.product', required=True, string="Items")
    parent_id = fields.Many2one('streamline.ame.material.take.off', required=True)
    required_qty = fields.Integer(string="Required Qty")
    received_qty = fields.Float(compute='compute_received_qty', string="Total Received Qty")
    purchase_line_id = fields.Many2one('purchase.order.line', 'PO Line')
    purchase_id = fields.Many2one('purchase.order', 'PO', related='purchase_line_id.order_id')
    purchased_qty = fields.Float("Purchased Qty", related='purchase_line_id.product_qty')
    price_unit = fields.Float("Price Unit", related='purchase_line_id.price_unit')

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
        for line in self:
            if not line.purchase_line_id:
                line.received_qty = 0
            else:
                move_objs = self.env['stock.move']
                move_ids = move_objs.search([('purchase_line_id', '=', line.purchase_line_id.id), ('state', '=', 'done')])
                received_qty = 0
                for move in move_ids:
                    received_qty += move.product_uom_qty
                line.received_qty = received_qty