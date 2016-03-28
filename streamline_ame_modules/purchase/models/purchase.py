from openerp import models, fields, api
from lxml import etree
import simplejson as json

class purchase_order(models.Model):
    _inherit = "purchase.order"
    
    @api.model
    def _default_receiver_name(self):
        partner_id = self.env.user.partner_id.id
        return partner_id
    
    @api.model
    def _default_receiver_hp(self):
        partner_id_phone = self.env.user.partner_id.mobile
        return partner_id_phone
    
    @api.model
    def _default_receiver_tel(self):
        partner_id_mobile = self.env.user.partner_id.phone
        return partner_id_mobile
    
    @api.model
    def _default_receiver_fax(self):
        partner_id_fax = self.env.user.partner_id.fax
        return partner_id_fax
    
    @api.model
    def _default_receiver_email(self):
        partner_id_email = self.env.user.partner_id.email
        return partner_id_email
    
    @api.onchange('receiver_id')
    def check_change_receiver_id(self):
        self.receiver_hp = self.receiver_id.mobile
        self.receiver_tel = self.receiver_id.phone
        self.receiver_fax = self.receiver_id.fax
        self.receiver_email = self.receiver_id.email
        
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(purchase_order, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        my_group_gid = self.env.ref('streamline_ame_modules.ame_general').id
        current_user_gids = self.env.user.groups_id.mapped('id')
        if my_group_gid in current_user_gids:
            doc = etree.XML(res['arch'])
            if view_type == 'form':
                nodes = doc.xpath("//form")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
            if view_type == 'tree':
                nodes = doc.xpath("//tree")
                for node in nodes:
                    node.set('create', 'false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
            res['arch'] = etree.tostring(doc)
        return res
    
    project_no = fields.Many2one('streamline.ame.project.project')
    receiver_id = fields.Many2one('res.partner', string="Receiver Name", default=_default_receiver_name)
    receiver_hp = fields.Char(string='Receiver HP', default=_default_receiver_hp)
    receiver_tel = fields.Char(string='Receiver Tel', default=_default_receiver_tel)
    receiver_fax = fields.Char(string='Receiver Fax', default=_default_receiver_fax)
    receiver_email = fields.Char(string='Receiver Email', default=_default_receiver_email)
