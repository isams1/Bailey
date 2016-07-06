# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm
from lxml import etree
import simplejson as json

class sale_order(models.Model):
    _inherit = "sale.order"

    project_no = fields.Many2one('streamline.ame.project.project', 'Project No', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    # @api.model
    # def create(self, vals):
    #     sale_id = super(sale_order, self).create(vals)
    #     self.action_send_mail(sale_id, vals)
    #     return sale_id

    def action_button_confirm(self, cr, uid, ids, context=None):
         for model_id in ids:
            vals = self.read(cr, uid, model_id, [], context)
            self.action_send_mail(cr, uid, model_id, vals)
         return super(sale_order, self).action_button_confirm(cr, uid, ids, context)
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(sale_order, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
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


    def action_send_mail(self, cr, uid, model_id, vals, context=None):
        if not context:
            context = {}

        model = 'sale.order'
        email_template_obj = self.pool.get('email.template')
        ir_model_data = self.pool.get('ir.model.data')

        template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=', model)])
        prod_template_id = ir_model_data.get_object_reference(cr, uid, 'streamline_ame_modules', 'email_template_create_sale')[1]
        if prod_template_id:
            template_ids = [prod_template_id]

        if not template_ids:
            return {}

        composer_obj = self.pool['mail.compose.message']
        composer_values = {}
        for template_id in template_ids:

            model_obj = self.pool.get(model)
            if model_id:
                email_ctx={
                    'default_model': model,
                    'default_res_id': model_id,
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                }
                template_values = [
                    template_id,
                    'comment',
                    model,
                    model_id,
                ]
                composer_values.update(composer_obj.onchange_template_id(cr, uid, None, *template_values, context=context).get('value', {}))
                if not composer_values.get('email_from'):
                    composer_values['email_from'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.email

                composer_values['body'] = composer_values['body']%vals
                for key in ['attachment_ids', 'partner_ids']:
                    if composer_values.get(key):
                        composer_values[key] = [(6, 0, composer_values[key])]

                composer_id = composer_obj.create(cr, uid, composer_values, context=email_ctx)
                composer_obj.send_mail(cr, uid, [composer_id], context=email_ctx)

        return True

sale_order()

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    remark = fields.Text('Remark')