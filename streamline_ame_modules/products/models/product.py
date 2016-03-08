# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm

def update_null_and_slash_codes(cr):
    """
    Updates existing codes matching the default '/' or
    empty. Primarily this ensures installation does not
    fail for demo data.
    :param cr: database cursor
    :return: void
    """
    cr.execute("UPDATE product_product "
               "SET default_code = 'PR' || id "
               "WHERE default_code IS NULL OR default_code = '/';")
    
    cr.execute("""
            update product_product
            set default_code = default_code || id
            where id in
            (
            select pp.id
            from product_product pp INNER JOIN 
            (
            select default_code, MAX(id) id
            from product_product
            where default_code in 
            (
            select default_code
            from product_product
            where default_code is not NULL
            group by default_code
            having count(1) > 1
            order by default_code
            )
            group by default_code
            order by 1
            ) tmp_pp on pp.default_code = tmp_pp.default_code and pp.id < tmp_pp.id
            order by 1
            )
        """)   

class product_product(models.Model):
    _inherit = "product.product"

    templ_minimum_ids = fields.One2many('product.minimum', 'product_id', string='Minimum Qty')
    default_code = fields.Char(
        string='Reference',
        size=64,
        select=True,
        required=True,
        default='/')
    
    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'Product Code must be unique!'),
    ]  
    
    @api.model
    def create(self, vals):
        if 'default_code' not in vals or vals['default_code'] == '/':
            vals['default_code'] = self.env['ir.sequence'].get(
                'product.product')
        if not self.env['res.users'].has_group('streamline_ame_modules.group_ame_create_product'):
            raise except_orm(_('Invalid Action!'), _('User is not in "Creating Product" group.'))
        product_id = super(product_product, self).create(vals)

        user = self.env['res.users'].browse(self._uid)
        tmpl = self.env['product.template'].browse(vals['product_tmpl_id'])
        vals = {'name': tmpl.name,
                'user': user.name,
                'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'default_code': vals.get('default_code', '')}
        self.action_send_mail(product_id, vals)
        return product_id

    @api.multi
    def write(self, vals):
        if not self.env['res.users'].has_group('streamline_ame_modules.group_ame_edit_product'):
            raise except_orm(_('Invalid Action!'), _('User is not in "Editing Product" group.'))

        for product in self:
            if product.default_code in [False, '/']:
                vals['default_code'] = self.env['ir.sequence'].get(
                    'product.product')
            super(product_product, product).write(vals)
        return True

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.default_code:
            default.update({
                'default_code': self.default_code + _('-copy'),
            })

        return super(product_product, self).copy(default)

    def check_inventory(self, cr, uid, product_ids, location_id, context=None):
        product_inventory = self._product_available(cr, uid,
                product_ids,
                context={'location': location_id})
        warning = {}
        for product in self.browse(cr, uid, product_ids, context):
            for minimum in product.product_tmpl_id.templ_minimum_ids:
                if minimum.location_id and minimum.location_id.id == location_id:
                    if product_inventory[product.id]['qty_available'] > minimum.quantity:
                        warning.update({product.id: minimum.quantity})
        return warning

    def action_send_mail(self, cr, uid, model_id, vals, context=None):
        if not context:
            context = {}

        model = 'product.product'
        email_template_obj = self.pool.get('email.template')
        ir_model_data = self.pool.get('ir.model.data')

        template_ids = email_template_obj.search(cr, uid, [('model_id.model', '=', model)])
        for email_template in ['email_template_create_product', 'email_template_create_product_purchaser']:
            prod_template_id = ir_model_data.get_object_reference(cr, uid, 'streamline_ame_modules', email_template)[1]
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
                    if email_template == 'email_template_create_product_purchaser':
                        try:
                            model, group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'warehouse_extended', 'group_ame_purchaser')
                        except ValueError:
                            return False
                        partner_ids = []
                        user_ids = self.pool.get('res.users').search(cr, uid, [('groups_id', '=', group_id)])
                        for user in self.pool.get('res.users').browse(cr, uid, user_ids):
                            partner_ids += [user.partner_id.id]
                        if partner_ids:
                             composer_values['partner_ids'] = partner_ids
                    # print vals
                    composer_values['body'] = composer_values['body']%vals
                    for key in ['attachment_ids', 'partner_ids']:
                        if composer_values.get(key):
                            composer_values[key] = [(6, 0, composer_values[key])]

                    composer_id = composer_obj.create(cr, uid, composer_values, context=email_ctx)
                    composer_obj.send_mail(cr, uid, [composer_id], context=email_ctx)

        return True

product_product()

class product_template(models.Model):
    _inherit = "product.template"
    
    templ_minimum_ids = fields.One2many('product.minimum', 'product_tmp_id', string='Minimum Qty')
    living_material_price = fields.Float('Living-Material', digits_compute=dp.get_precision('Product Price'))
    living_labour_price = fields.Float('Living-Labour', digits_compute=dp.get_precision('Product Price'))
    machinery_material_price = fields.Float('Machinery-Material', digits_compute=dp.get_precision('Product Price'))
    machinery_labour_price = fields.Float('Machinery-Labour', digits_compute=dp.get_precision('Product Price'))
    living_material_by_ame = fields.Boolean('By AME')
    living_labour_by_ame = fields.Boolean('By AME')
    machinery_material_by_ame = fields.Boolean('By AME')
    machinery_labour_by_ame = fields.Boolean('By AME')
    active = fields.Boolean('Active', default=False)
    loc_case = fields.Char('Level', size=16)
    loc_area = fields.Char('Area', size=16)

    @api.multi
    def write(self, vals):
        if not self.env['res.users'].has_group('streamline_ame_modules.group_ame_edit_product'):
            raise except_orm(_('Invalid Action!'), _('User is not in "Editing Product" group.'))
        return super(product_template, self).write(vals)

    @api.model
    def create(self, vals):
        if not self.env['res.users'].has_group('streamline_ame_modules.group_ame_create_product'):
            raise except_orm(_('Invalid Action!'), _('User is not in "Creating Product" group.'))
        return super(product_template, self).create(vals)

product_template()    