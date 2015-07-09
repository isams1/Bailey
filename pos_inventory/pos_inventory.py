# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Till Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp import netsvc

class pos_order(osv.Model):

    _inherit = "pos.order"
    _description = "Point of Sale Inherited"

    _columns = {
            'procurement_group_id': fields.many2one('procurement.group', 'Procurement group', copy=False),
        }

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []

        for order in self.browse(cr, uid, ids, context=context):
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery',False),
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

            move_list = []
            for line in order.lines:
                if line.product_id and line.product_id.type == 'service':
                    continue

                if line.qty < 0:
                    location_id, destination_id = destination_id, location_id

                move_id = move_obj.create(cr, uid, {
                    'name': line.product_id.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'picking_type_id': picking_type.id, 
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.qty),
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': destination_id
                }, context=context)
                move_list.append(move_id)

                vals = self._prepare_procurement_group(cr, uid, order, context=context)
                if not order.procurement_group_id:
                    group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                    order.write({'procurement_group_id': group_id}, context=context)

                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, order.date_order, destination_id, group_id=group_id,context=context))
                print "proc_id:::::::::::::::::",proc_id
                proc_ids.append(proc_id)
            #Confirm procurement order such that rules will be applied on it
            #note that the workflow normally ensure proc_ids isn't an empty list
            procurement_obj.run(cr, uid, proc_ids, context=context)

            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
                picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                move_obj.force_assign(cr, uid, move_list, context=context)
                move_obj.action_done(cr, uid, move_list, context=context)
        return True

    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, destination_id, group_id=False, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if order.partner_id.id:
            partner_dest_id = self.pool.get('res.partner').address_get(cr, uid, [order.partner_id.id], ['delivery'])['delivery']
        else:
            partner_dest_id = False
        return {
            'name': line.product_id.name,
            'origin': order.name,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.qty,
            'product_uom': line.product_id.uom_id.id,
            'product_uos_qty': line.qty,
            'product_uos': line.product_id.uom_id.id,
            'company_id': order.company_id.id,
            'warehouse_id' : warehouse_ids and warehouse_ids[0], 
            'move_id': move_id,
            'group_id': group_id,
            'location_id': destination_id,
            'partner_dest_id' : partner_dest_id or False,
        }

    def _prepare_procurement_group(self, cr, uid, order, context=None):
        return {'name': order.name, 'partner_id': order.partner_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
