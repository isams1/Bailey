# -*- coding: utf-8 -*-
from openerp import models, fields, api
from lxml import etree
import simplejson as json


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(account_invoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
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

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(purchase_order_line, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
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
