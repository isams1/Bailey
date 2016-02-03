from openerp.osv import fields, osv
from openerp.tools.translate import _
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):

        warning = {}
        if context.get('location_id', False):
            warning = self.pool.get('product.product').check_inventory(cr, uid, [product_id], context['location_id'], context)
        result = super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)
        if warning:
            result['warning'] = {'title': _('Warning!'), 'message': _('Stock on hand > stock minimum.')}
        return result