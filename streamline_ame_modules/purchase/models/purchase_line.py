from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft', context=None):

        product_inventory = False
        if context.get('location_id', False):
            product_inventory = self.pool.get('product.product')._product_available(cr, uid, [product_id],
                                                        context={'location': context['location_id']})
        result = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty,
                                                                      uom_id,
                                                                      partner_id, date_order, fiscal_position_id,
                                                                      date_planned,
                                                                      name, price_unit, state, context)

        product = self.pool.get('product.product').browse(cr, uid, product_id, context)
        if product_inventory and product_inventory[product.id]['qty_available'] > 0:
            result['warning'] = {'title': _('Warning!'), 'message': _('Item %s have a total qty of %s %s.' % (
            product.name, product_inventory[product.id]['qty_available'], product.uom_id.name))}
        return result
