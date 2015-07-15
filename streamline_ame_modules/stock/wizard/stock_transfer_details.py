# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime

class stock_transfer_details(models.TransientModel):
    _inherit = "stock.transfer_details"
    
    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                lot_id = prod.lot_id.id
                product_qty = prod.quantity
                
                if self.picking_id.picking_type_id.code == 'incoming':
                    production_lot_obj = self.env['stock.production.lot']
                    if lot_id == False:
                        lot_id = production_lot_obj.create({'product_id': prod.product_id.id}).id
                        
                if self.picking_id.picking_type_id.code == 'outgoing':
                    if lot_id != False:
                        create_date = False
                        for move in self.picking_id.move_lines:
                            if move.product_id.id == prod.product_id.id:
                                for quant in move.reserved_quant_ids:
                                    if create_date == False:
                                        lot_id = quant.lot_id.id
                                        create_date = quant.lot_id.create_date
                                    elif quant.create_date >= create_date:
                                        lot_id = quant.lot_id.id
                                        create_date = quant.lot_id.create_date
                                    else:
                                        pass
                    else:
                        create_date = False
                        for move in self.picking_id.move_lines:
                            if move.product_id.id == prod.product_id.id:
                                for quant in move.reserved_quant_ids:
                                    pack_datas = {
                                        'product_id': prod.product_id.id,
                                        'product_uom_id': prod.product_uom_id.id,
                                        'product_qty': quant.qty,
                                        'package_id': False,
                                        'lot_id': quant.lot_id.id,
                                        'location_id': prod.sourceloc_id.id,
                                        'location_dest_id': prod.destinationloc_id.id,
                                        'result_package_id': False,
                                        'date': prod.date if prod.date else datetime.now(),
                                        'owner_id': False,
                                        'processed': 'false',
                                        'picking_id': self.picking_id.id,
                                    }
                                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                                    processed_ids.append(packop_id.id)
                        continue                
                    
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': product_qty,
                    'package_id': prod.package_id.id,
                    'lot_id': lot_id if lot_id else False,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.with_context(no_recompute=True).write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        packops.unlink()

        # Execute the transfer of the picking
        self.picking_id.do_transfer()

        return True