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
import time
from openerp import netsvc, tools
from openerp.tools.translate import _
from openerp import workflow
from openerp import SUPERUSER_ID
import os

class pos_config(osv.osv):
    _inherit = 'pos.config'

    _columns = {
        'display_send_to_kitchen':fields.boolean("Display Send To Kitchen Button", help="If Display Send To kitchen Button is true than pos shows a send to kitchen button."),
        'display_print_receipt':fields.boolean("Display Print Receipt Button", help="If Display Print Receipt Button is true than pos shows a print receipt button."),
        'customer_receipt':fields.boolean("Print Customer Receipt"),
        'allow_salesman':fields.boolean("Allow Salesman", help="If button is true than salesman is allowed in pos."),
        'manage_delivery': fields.boolean("Manage Delivery"),
        'pincode': fields.boolean("Pin Code"),
        'show_area': fields.boolean("Display Area"),
    }

    _defaults = {
        'display_send_to_kitchen' : 1,
        'display_print_receipt' : 1,
        'allow_salesman' : 1,
        'show_area':1,
        'customer_receipt':1,
        'manage_delivery' : 1,
    }

class table_reserved(osv.osv):
    _name = "table.reserverd"

    _columns = {
        "table_id":fields.many2one("table.master", "Table", required=True),
        "reserver_seat":fields.integer("Reserved Seat", required=True),
        "order_id":fields.many2one("pos.order", "POS Order"),
        "area_id":fields.related("table_id","area_id", type='many2one', relation='area.area', string="Area"),
    }

class area_area(osv.osv):
    _name = "area.area"

    _columns = {
        "name": fields.char("Name", required=True),
        "code":fields.char("Code")
    }

class pos_order(osv.osv):
    _inherit = "pos.order"
    
    global expand_all_product_ids, expand_four_product_ids, order_ids
    expand_all_product_ids = []
    expand_four_product_ids = []
    order_ids = []
    
    def get_product_price(self,cr,uid,price_list_id,product_ids,qty,context=None):
        product_price_list_object = self.pool.get('product.pricelist')
        res = []
        for product_id in product_ids :
            res.append({'id':product_id,'data':product_price_list_object.price_get(cr,uid,price_list_id,product_id,qty)})
        return res
    
    def product_line(self, cr, uid, ids, name, arg, context=None):
        res1 = {}
        count = 0
        for order in self.browse(cr, uid, ids, context=context):
            res = []
            str1 = ""
            for line in order.lines :
#                 if line.order_line_state_id.id != 3 and line.order_line_state_id.id != 4 :
                     count = count + 1
                     if expand_all_product_ids == [] and expand_four_product_ids == []  and count <= 4:
                         str1 = line.product_id.name + "____" + str(line.qty) + "-" + str(line.id) + '-' + str(line.order_line_state_id.id) + '-'+ str(line.property_description) 
                     if [[order.id]] == expand_all_product_ids :
                         str1 = line.product_id.name + "____" + str(line.qty) + "-" + str(line.id) + '-' + str(line.order_line_state_id.id) + '-'+ str(line.property_description) 
                     if [[order.id]] == expand_four_product_ids and count <= 4 :
                         str1 = line.product_id.name + "____" + str(line.qty) + "-" + str(line.id) + '-' + str(line.order_line_state_id.id) + '-'+ str(line.property_description) 
                     res.append(str1)
            count = 0
            if expand_all_product_ids :
              expand_all_product_ids.remove(ids)
            if expand_four_product_ids :
              expand_four_product_ids.remove(ids)
            res1[order.id] = res  
        return res1

    
    def get_table_name(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            tab_name = ''
            for table in order.reserved_table_ids:
                if table.table_id:
                    tab_name += table.table_id.name +" "
            res[order.id] = tab_name
        return res

    def get_done_orderline(self, cr, uid, ids, context = None):
        order_data = [] 
        for order in self.browse(cr, uid, ids, context = context):
            line_ids = []
            for line in order.lines:
                if line.order_line_state_id.id == 3:
                    line_ids.append(line.id)
            if line_ids:
                order_data.append({"id":order.id, "line_ids":line_ids})
        if order_data:
            return order_data or False

    def show_all_product(self, cr, uid, ids, context=None):
       if ids in order_ids:
           order_ids.remove(ids)
           expand_four_product_ids.append(ids)
       else:
           order_ids.append(ids)
           expand_all_product_ids.append(ids)
       return True

    _columns = {
        'table_name': fields.function(get_table_name, type='char', string='Table Name', store=True),
#        'table_ids':fields.many2many("table.master", "rel_table_pos_order", "order_id", "table_id", "Tables"),
        'reserved_table_ids':fields.one2many("table.reserverd", "order_id", "Reserved Table"),
        'pflag' : fields.boolean('Flag'),
        'use_order': fields.boolean('orders'),
        'parcel':fields.char("Parcel Order",size=32),
        'driver_name': fields.many2one('res.users', "Delivery Boy"),
        'phone':fields.char("Customer Phone Number", size=128),
        'color':fields.integer("Color Index"),
        'split_order' : fields.boolean('split'),
        'product_details': fields.function(product_line, type='one2many', relation="pos.order.line", string='details1', store=False),
        'order_line_status':fields.char("Orderline Status"),
    }

    _defaults = {
        'pflag' : 0,
        'use_order' : True,
        'order_line_status':'draft',
    }

    def remove_order(self, cr, uid, ids, second_order_id = False, context = None):
        if ids and second_order_id:
            line_ids = [line.id for line in self.browse(cr, uid, second_order_id, context = context).lines]
            self.pool.get("pos.order.line").write(cr, uid, line_ids, {"order_id" : ids[0]})
            workflow.trg_validate(uid, 'pos.order', second_order_id, 'cancel', cr)
        if not ids and second_order_id:
            workflow.trg_validate(uid, 'pos.order', second_order_id, 'cancel', cr)
        return True

    def pole_display(self, cr, uid, product, price, validate = False,context = None):
        import serial
        value = []
        temp = []
        new_list = []
        lon = []
        upper_line = []
        sec_line = []
        rem_space = 20
        total_len_upper = 0
        final = 0
        global pos
        def price_calculation():
            sum = 0.00
            for i in range(0,len(price)):
                pos = price[i].index('$')
                new_price = price[i].replace("$", " ")
                p = float(new_price)
                sum += p
                new_sum = format(sum, '.2f')
                ppp = list(new_sum)
                ppp.insert(pos,'$')
                delimiter = ''
                total = delimiter.join(ppp)
                if total not in lon:
                    lon.append(total)
            return lon

        check = os.path.exists("/dev/ttyACM0")
        if check:
            serial = serial.Serial(port="/dev/ttyACM0", baudrate=9600)
            try:
                if serial.isOpen():
                    if not validate:
                        #serial.write(chr(0x1B)+chr(0x45)+chr(0x58)+chr(0x34))
                        #serial.write(chr(0x0C))
                        #serial.write(chr(0x1B) + chr(0x43) + chr(0x1) + chr(0x01))
                        serial.write(chr(0x1F)+chr(0x24)+chr(0x1)+chr(0x1))
                        for i in range(0, len(product)):
                            serial.write(chr(0x0C))
                            temp_price = price[i].translate(None, " ")
                            if " " in product[i]:
                                temp = product[i].split(" ")
                                temp.append(temp_price)
                                for i in range(0, len(temp)):
                                    len_prod = len(temp[i])
                                    if (rem_space >= len_prod) and (len(temp)):
                                        upper_line.append(temp[i])
                                        rem_space = rem_space - len_prod - 1
                                        total_len_upper += len_prod
                                    else:
                                        sec_line.append(temp[i])
                                        final = 20 - total_len_upper
                                        votr = sec_line[0].rjust(final)
                            else:
                                check = len(product[i] + " " + temp_price)
                                if check < rem_space:
                                    serial.write(product[i] + " " + temp_price)
                                else:
                                    space = 20 - len(product[i])
                                    new_space = len(product[i]) + space
                                    temp_price = temp_price.rjust(new_space, " ")   
                                    serial.write(product[i] + " " + temp_price) 
                        upper_line = " ".join(upper_line)
                        space = 20 - (len(upper_line))
                        sec_line = " ".join(sec_line)
                        new_space = len(sec_line) + space
                        sec_line = sec_line.rjust(new_space," ")
                        serial.write(upper_line + sec_line)
                    else:
                        print "yes i am here"
                        #serial.write(chr(0x1B) + chr(0x43) + chr(0x1) + chr(0x01))
                        for i in range(0,len(product)):
                            if " " in product[i]:
                                del upper_line[:]
                                del sec_line[:]
                                aval_space = 20
                                temp = product[i].split(" ")
                                for i in range(0, len(temp)):
                                    len_each = len(temp[i])
                                    if (aval_space >= len_each) and (len(temp)):
                                        upper_line.append(temp[i])
                                        aval_space = aval_space - len_each - 1
                                        len_upper = len_each
                                    else:
                                        sec_line.append(temp[i])
                                        final = 20 - len_upper
                                        votr = sec_line[0].rjust(final)

                                upper = " ".join(upper_line)
                                space = 20 - (len(upper))
                                if sec_line:
                                    second = " ".join(sec_line)
                                    new_space = len(second) + space
                                    second = second.rjust(new_space," ")
                                    new= upper + " " + second
                                    new_list.append(new)
                                else:
                                    new_list.append(upper)
                            else:
                                new_list.append(product[i])
                                
                        #serial.write(chr(0x1B) + chr(0x43) + chr(0x1) + chr(0x01))
                        serial.write(chr(0x1F)+chr(0x24)+chr(0x1)+chr(0x1))
                        serial.write(chr(0x0C))
                        a = price_calculation()
                        b = new_list
                        for i in range(0,len(new_list)):
                            serial.write(chr(0x0C))
                            diff = 40 - len(new_list[i])
                            new_diff = diff - len(a[i])
                            send = a[i].rjust(new_diff)
                            serial.write(new_list[i] + " " + send)
                            for j in range(0,5000000):
                                pass
            except:
                print "ERROR: Device not connected"
            return True
        else:
            return False

    def close_order(self, cr, uid, order_id, context = None):
        for order in self.browse(cr, uid, order_id, context = context):
            line_ids = []
            for line in order.lines:
                if line.order_line_state_id.id == 3 or line.order_line_state_id.id != 1:
                    line_ids.append(line.id)
        if line_ids:
            return False
        if order_id:
            for order in self.browse(cr, uid, order_id, context = context):
                for res_table in order.reserved_table_ids:
                    if (res_table.table_id.available_capacities - res_table.reserver_seat) == 0:
                            self.pool.get("table.master").write(cr, uid, res_table.table_id.id, {'state': 'available','available_capacities': res_table.table_id.available_capacities - res_table.reserver_seat   })
                    else:
                        if (res_table.table_id.available_capacities - res_table.reserver_seat) > 0:
                            self.pool.get("table.master").write(cr, uid, res_table.table_id.id, {'state': 'available','available_capacities': res_table.table_id.available_capacities - res_table.reserver_seat })
            order_id = order_id[0]
            line_ids = [line.id for line in self.browse(cr, uid, order_id, context = context).lines]
            self.pool.get("pos.order.line").write(cr, uid, line_ids, {"order_id":order_id})
            workflow.trg_validate(uid, 'pos.order', order_id, 'cancel', cr)
        return True

    def get_draft_state_order(self, cr, uid, context=None):
        domain = [('state','=', 'draft'), ('reserved_table_ids', '!=', False)]
        if uid != SUPERUSER_ID:
            domain.extend([('user_id', '=', uid)])
        draft_order_ids = self.search(cr, uid, domain, context=context)
        table_obj = self.pool.get("table.master")
        #draft_order_ids = self.search(cr, uid,[('user_id', '=', uid), ('state','=', 'draft'), ('reserved_table_ids', '!=', False)])
        if draft_order_ids:
            orders = []
            for b_order in self.browse(cr, uid, draft_order_ids, context=context):
                order = {
                         'id': b_order.id,
                         'name': b_order.name,
                         'pos_reference': b_order.pos_reference,
                         'pricelist_id': b_order.pricelist_id.id,
                         'user_id': b_order.user_id.id,
                         'partner_id': b_order.partner_id.name or False
                        }
                table_ids = []
                table_name = ''
                table_data = []
                reserved_seat = ''
                table_ids = []
                for reserve in b_order.reserved_table_ids:
                    table = table_obj.browse(cr, uid, reserve.table_id.id)
                    table_ids.append(table.id)
                    reserved_seat += str(table.id)+"/"+str(reserve.reserver_seat)+"_"
                    table_name += table.name+"/"+str(reserve.reserver_seat) + ' '
                    table_data.append({"reserver_seat":reserve.reserver_seat, 'table_id':table.id})
                order.update({'table_ids': table_ids})
                order.update({'table_name': table_name})
                order.update({'reserved_seat':reserved_seat, 'table_data': table_data})
                lines = []
                for line in b_order.lines:
                    wait = False
                    if line.order_line_state_id.id == 5:
                         wait = True
                    lines.append({'id':line.id,
                                  'product_id':line.product_id.id,
                                  'qty':line.qty,
                                  'discount':line.discount,
                                  'price_unit':line.price_unit,
                                  'property_description':line.property_description,
                                  'flag':True,
                                  'name':line.name,
                                  'wait': wait
                                  })
                order.update({'lines':lines})
                orders.append(order)
            return orders
        return True

    def check_group_pos_cashier_user(self, cr, uid, puser, context=None):
        mod_obj = self. pool.get('ir.model.data')
        grp_result = mod_obj.get_object(cr, uid, 'point_of_sale_table', 'group_pos_cashier')
        user_add = [user.id for user in grp_result.users]
        for user in mod_obj.get_object(cr, uid, 'point_of_sale', 'group_pos_manager').users:
            if puser in user_add:
                return True 
        return False
    
    def check_group_pos_delivery_boy(self, cr, uid, puser, context=None):
        mod_obj = self. pool.get('ir.model.data')
        grp_result = mod_obj.get_object(cr, uid, 'point_of_sale_table', 'group_pos_delivery_boy')
        user_add = [user.id for user in grp_result.users]
        for user in mod_obj.get_object(cr, uid, 'point_of_sale', 'group_pos_manager').users:
            if puser in user_add:
                return True 
        return False

    def reassign_table(self, cr, uid, booked_table):
        table_obj = self.pool.get('table.master')
        if booked_table and booked_table.split('_'):
            for booked in booked_table.split('_'):
                if booked:
                    table_id = int(booked.split('/')[0])
                    qty = int(booked.split('/')[1])
                    table_data = table_obj.browse(cr, uid, table_id)
                    table_obj.write(cr, uid, [table_id], {'available_capacities': table_data.available_capacities - int(qty), 'state': 'available'})
        return True

    def create_from_ui(self, cr, uid, orders, kitchen=False,confirm = False, context=None):
        order_ids = []
        pos_line_object = self.pool.get('pos.order.line')
        table_reserved_obj = self.pool.get("table.reserverd")
        session_obj = self.pool.get('pos.session')
        shop_obj = self.pool.get('sale.shop')
        for tmp_order in orders:
            to_invoice = tmp_order.get('to_invoice')
            if tmp_order.get('data'):
                order = tmp_order['data']
            else:
                order = tmp_order
            user_id = order.get('user_id')
        sql = """
            SELECT id
            FROM pos_session
            WHERE user_id = %d and state = 'opened';

        """ % (int(user_id))
        cr.execute(sql)
        tmp_data = cr.fetchall()
        if not tmp_data:
            raise osv.except_osv(_('error!'),
                                _("No Point Of Sale Found For User."))
        else:
            if tmp_data:
                order.update({"pos_session_id":tmp_data[0][0]})
            if order.get('id'):
                created_order = self.browse(cr, uid, order.get('id'), context=context)
                if order.get('user_id') and created_order.user_id.id != order.get('user_id'):
                    self.write(cr, uid, created_order.id, {'user_id':order.get('user_id')}, context=context)
                line_ids = [line.id for line in created_order.lines]
                table_data = order.get("table_data")
                reserve_table_ids = []
                if table_data:
                    self.write(cr, uid, order.get('id'), {'reserved_table_ids': [(5,0)]}, context = context)
                    for reserve in table_data:
                        reserve.update({"order_id":order.get('id')})
                        reserv_id = self.pool.get("table.reserverd").create(cr, uid, reserve, context = context)
                        reserve_table_ids.append((4,reserv_id))
                        self.write(cr, uid, [order.get('id')], {'reserved_table_ids': reserve_table_ids}, context = context)
                if tmp_order.get('partner_id'):
                    self.write(cr, uid, [order.get('id')], {'partner_id': tmp_order.get('partner_id')}, context = context)
                if line_ids:
                    for line in order.get('lines'):
                        if line[2] and line[2].get('line_id') :
                            pos_line_object.write(cr, uid, [int(line[2].get('line_id'))], {'property_description':line[2].get('property_description') or '',
                                                         'discount':line[2].get('discount'),
                                                         'price_unit':line[2].get('price_unit'),
                                                        'product_id':line[2].get('product_id'),
                                                        'product_ids': line[2].get('product_ids'),
                                                        'qty':line[2].get('qty'),
                                                        'order_line_state_id': line[2].get('wait_text') and 5 or 1,
                                                        'flag':True}, context = context)
                for line in order.get('lines'):
                    if line[2] and not line[2].get('line_id'):
                        pos_line_object.create(cr, uid, {'property_description':line[2].get('property_description') or '',
                                                             'discount':line[2].get('discount'),
                                                             'price_unit':line[2].get('price_unit'),
                                                            'product_id':line[2].get('product_id'),
                                                            'product_ids': line[2].get('product_ids'),
                                                            'qty':line[2].get('qty'),
                                                            'order_id':order.get('id'),
                                                            'flag':True,
                                                            'order_line_state_id': line[2].get('wait_text') and 5 or 1,
                                                            }, context = context)
                if kitchen:
                    created_order = self.browse(cr, uid, order.get('id'), context=context)
                    line_ids = [line.id for line in created_order.lines]
                    return [order.get('id'), line_ids]
                else: 
                    order_id = order.get('id')
            else:
                table_data = order.get("table_data")
                tables = []
                if table_data:
                    for reserve in table_data:
                        table_id = reserve.get('table_id')
                        reserv_id = self.pool.get("table.reserverd").create(cr, uid, reserve, context = context)
                        tables.append((4,reserv_id))
                    for line in order.get('lines'):
                        line[2].update({'flag':True,'order_line_state_id':line[2].get('wait_text') and 5 or 1})
                    order_id = self.create(cr, uid, {
                        'name': order['name'],
                        'phone': order['phone'] or False,
                        'split_order': order.get('split_order',False),
                        'user_id': order['user_id'] or False,
                        'partner_id': order.get('partner_id'),
                        'pricelist_id': order.get('pricelist_id',False),
                        'session_id': order['pos_session_id'],
                        'lines': order['lines'],
                        'pos_reference':order['name'],
                        'reserved_table_ids': tables,
                    }, context)

                if not table_data:
                    for line in order.get('lines'):
                        line[2].update({'flag':True,'order_line_state_id':line[2].get('wait_text') and 5 or 1})
                    order_id = self.create(cr, uid, {
                        'name': order['name'],
                        'user_id': order['user_id'] or False,
                        'driver_name': order.get('driver_name',False),
                        'phone': order.get('phone',False),
                        'split_order': order.get('split_order',False),
                        'partner_id': order.get('partner_id'),
                        'pricelist_id': order.get('pricelist_id',False),
                        'session_id': order['pos_session_id'],
                        'lines': order['lines'],
                        'pos_reference':order['name'],
                        'pflag': order.get('pflag', False),
                        'parcel':order.get('parcel', False),
                    }, context)

                created_order = self.browse(cr, uid, order_id, context=context)
                line_ids = [line.id for line in created_order.lines]
                if kitchen:
                    return [order_id, line_ids]
            if not kitchen and not confirm:
                for payments in order['statement_ids']:
                    payment = payments[2]
                    self.add_payment(cr, uid, order_id, {
                        'amount': payment['amount'] or 0.0,
                        'payment_date': payment['name'],
                        'statement_id': payment['statement_id'],
                        'payment_name': payment.get('note', False),
                        'journal': payment['journal_id']
                    }, context=context)

                if order['amount_return']:
                    session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)
                    cash_journal = session.cash_journal_id
                    if not cash_journal:
                        cash_journal_ids = filter(lambda st: st.journal_id.type == 'cash', session.statement_ids)
                        if not len(cash_journal_ids):
                            raise osv.except_osv(_('error!'),
                                _("No cash statement found for this session. Unable to record returned cash."))
                        cash_journal = cash_journal_ids[0].journal_id
                    self.add_payment(cr, uid, order_id, {
                        'amount':-order['amount_return'],
                        'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'payment_name': _('return'),
                        'journal': cash_journal.id,
                    }, context=context)
                order_ids.append(order_id)
                workflow.trg_validate(uid, 'pos.order', order_id, 'paid', cr)
            else:
                created_order = self.browse(cr, uid, order_id, context=context)
                line_ids = [line.id for line in created_order.lines]
                return [order_id, line_ids]
                #order_ids.append(order_id)

            if to_invoice:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')
            return order_ids

    def action_paid(self, cr, uid, ids, context=None):
        res = super(pos_order, self).action_paid(cr, uid, ids, context=context)
        table_obj = self.pool.get("table.master")
        analytic_line_obj = self.pool.get('account.analytic.line')
        today_date = time.strftime('%Y-%m-%d')
        for order in self.browse(cr, uid, ids, context = context):
            if not order.split_order:
                for res_table in order.reserved_table_ids:
                    if (res_table.table_id.available_capacities - res_table.reserver_seat) == 0:
                            table_obj.write(cr, uid, res_table.table_id.id, {'state' : 'available','available_capacities' : res_table.reserver_seat - res_table.table_id.available_capacities })
                    else:
                        if (res_table.table_id.available_capacities - res_table.reserver_seat) > 0:
                            table_obj.write(cr, uid, res_table.table_id.id, {'state' : 'available','available_capacities': res_table.reserver_seat - res_table.table_id.available_capacities})
        return res

class table_master(osv.osv):
    _name = 'table.master'

    _description = "Table Master"

    _columns = {
        'name': fields.char('Description', required=True, size=64, select=1),
        'code': fields.char('Code', size=64, required=True),
        'capacities':fields.integer('Capacities'),
        'state':fields.selection([('reserved','Reserved'),('available','Available')], 'State', required=True),
        'users_ids':fields.many2many('res.users', 'rel_table_master_users', 'table_id', 'user_id', 'User'),
        'available_capacities':fields.integer('Reserved Seat', readonly=True),
        'area_id':fields.many2one("area.area", "Area", required=True),
    }
    _defaults = {
        'state':'available',
        'available_capacities' : 0,
    }
    
    _sql_constraints = [
        ('code_uniq', 'unique(code)','Table code must be unique!'),
    ]

    def get_waiter_list(self, cr, uid,context=None):
        table_ids = self.search(cr, uid, [], context = context)
        waiter_list = []
        final_list = []
        if table_ids:
            for table in self.browse(cr, uid, table_ids, context = context):
                for table_user in table.users_ids:
                    if table_user.id not in waiter_list:
                        waiter_list.append(table_user.id)
                        waiter_list_temp = {'id':table_user.id,'name':table_user.name}
                        final_list.append(waiter_list_temp)
            return final_list

    def action_available(self, cr, uid, ids, context=None):
        if ids:
            reserve_table_obj = self.pool.get("table.reserverd")
            for table in self.browse(cr, uid, ids, context = context):
                reserve_ids = reserve_table_obj.search(cr, uid,[('table_id', '=', table.id), ("order_id.state", "=", "draft")])
                if reserve_ids:
                    raise osv.except_osv(_('Warning!'),_('Table is not empty!'))
                else:
                    self.write(cr, uid, [table.id], {'state': 'available', 'available_capacities': 0}, context=context)
        return True

class pos_category(osv.osv):

    _inherit = "pos.category"

    _columns = {
            "split":fields.boolean("Print Separate Receipt", help="print category wise product in pos receipt."),
    }

    def sort_categ_tree(self, cr, uid, context=None):
        categ_ids = self.search(cr, uid, [('split', '=', True)])
        prod_categ_ids = {}
        spit_categ_name = {}
        prod_categ_lst = []
        if categ_ids:
            for c_id in categ_ids:
                categ_name = self.browse(cr, uid, c_id, context).name
                seq = self.browse(cr, uid, c_id, context).sequence
                prod_categ_ids.update({c_id : {'id' : self.search(cr, uid, [('parent_id', 'child_of', [c_id])]), 'name': categ_name, 'categ_id': c_id,'seq':seq}})
        for val in prod_categ_ids.values():
            prod_categ_lst.append(val)
        prod_categ_lst = sorted(prod_categ_lst, key=itemgetter('seq'))
        return prod_categ_lst

    def get_category_tree(self, cr, uid, context = None):
        categ_ids = self.search(cr, uid, [('split', '=', True)])
        prod_categ_ids = {}
        categ_child_ids = []
        if categ_ids:
            for c_id in categ_ids:
                category_id = self.search(cr,uid,[('parent_id','child_of',[c_id])])
                categ_child_ids.extend(category_id)
                categ_name = self.browse(cr, uid, c_id, context).name
                prod_categ_ids.update({c_id : {'id' : category_id, 'name': categ_name, 'categ_id': c_id}})
        if prod_categ_ids:
            all_cate_ids = self.search(cr, uid, [])
            difference_ids = list(set(all_cate_ids).difference(categ_child_ids))
            prod_categ_ids.update({'other' : {'id' : difference_ids, 'name': 'Others', 'categ_id': 'other'},'all' : {'id' : all_cate_ids, 'name': 'All', 'categ_id': 'all'}})
        if not prod_categ_ids:
            all_cate_ids = self.search(cr, uid, [])
            prod_categ_ids.update({'all' : {'id' : all_cate_ids, 'name': 'All', 'categ_id': 'all'}})
        return prod_categ_ids

class product_description(osv.osv):
    _name = "product.description"

    _columns = {
        "name": fields.char("Name", required=True),
    }

class product_template(osv.Model):
    _inherit = "product.template"

    _columns = {
        'is_product_description': fields.boolean("Display Description", help="If free text is true than user can add information about product."),
        'is_product_wait': fields.boolean("Display Wait Button" , help="If wait is true than product is placed in waiting state in kitchen receipt."),
        'is_pizza': fields.boolean("Is Pizza"),
        'large_pizza_price': fields.float(string='Large Pizza Price'),
    }

class pos_order_line_state(osv.osv):
    _name = "pos.order.line.state"

    _description = "Pos Order Line State"

    _columns = {
        'name':fields.char('Name', size=18),
        'sequence':fields.integer('Sequence'),
    }

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"

    _columns = {
        'order_name': fields.related('order_id', 'pos_reference', type="char", string="Order Name", relation='pos.order'),
        'table_name': fields.related('order_id', 'table_name', type="char", string="Tables", relation='pos.order'),
        'parcel': fields.related('order_id', 'parcel', string="Parcel", type="char", relation='pos.order'),
        'partner_id': fields.related('order_id', 'partner_id', 'name', type="char", string="Customer", relation='pos.order'),
        'flag': fields.boolean('flag'),
        'color': fields.integer('Color Index'),
        'sequence': fields.related("product_id", "pos_categ_id", "sequence" , type="integer", string ="Sequence", store=True),
        'categ_id': fields.related("product_id", "pos_categ_id", relation='pos.category', type='many2one', string="Category Name", store=True),
        'property_description': fields.text('Property Description'),
        'product_ids': fields.many2many('product.product', 'product_pos_line_rel', 'product_id', 'line_id', 'Product'),
        'order_line_state_id': fields.many2one('pos.order.line.state', "Order Line State"),
        'table_ids': fields.related('order_id', 'table_ids', type="many2many", string="Tables", relation='table.master'),
        'wait_text' : fields.boolean('Free text'),
    }

    def orderline_state_id (self, cr, uid, pids, context=None):
        if pids != None:
            return self.browse(cr,uid,pids,context=context).order_line_state_id.id
        else :
            return True

    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        line_stage_obj = self.pool.get('pos.order.line.state')
        result = []
        line_stage_ids = line_stage_obj.search(cr, uid, [], order='sequence', context=context)
        for line_stage in line_stage_obj.browse(cr, uid, line_stage_ids, context=context):
            result.append((line_stage.id, line_stage.name))
        return result, {}

    _group_by_full = {
        'order_line_state_id': _read_group_stage_ids,
    }

    _order = "order_id,sequence"

    def forward_change_state(self, cr, uid, ids, context = None):
        o_l_state_obj = self.pool.get("pos.order.line.state")
        for order_lint in self.browse(cr, uid, ids, context = context):
            o_l_seq = o_l_state_obj.search(cr, uid, [('sequence', '>', order_lint.order_line_state_id.sequence)])
            sequence = []
            sequence_data = []
            for state_seq in o_l_state_obj.browse(cr, uid, o_l_seq, context = context):
                sequence.append(state_seq.sequence)
                sequence_data.append({'id':state_seq.id, 'sequence': state_seq.sequence})
            if sequence and type(sequence) is list:
                sequence.sort()
                for s_d in sequence_data:
                    if(s_d.get('sequence') == sequence[0]):
                        if sequence.__len__() == 1:
                            self.write(cr, uid, order_lint.id, {'order_line_state_id':s_d.get('id')}, context = context )
                            return {
                                'name': _('Kitchen Screen'),
                                'view_type': 'kanban',
                                'view_mode': 'kanban,tree,form',
                                'res_model': 'pos.order.line',
                                'view_id': False,
                                'tag':'reload',
                                'type': 'ir.actions.act_window',
                                'context':context,
                                'domain':[('order_id.state', '=', 'draft'), ('order_line_state_id','!=',4)],
                            }
                        else:
                            self.write(cr, uid, order_lint.id, {'order_line_state_id':s_d.get('id')}, context = context )
                            return {
                                'name': _('Kitchen Screen'),
                                'view_type': 'kanban',
                                'view_mode': 'kanban,tree,form',
                                'res_model': 'pos.order.line',
                                'view_id': False,
                                'tag':'reload',
                                'type': 'ir.actions.act_window',
                                'context':context,
                                'domain':[('order_id.state', '=', 'draft'), ('order_line_state_id','!=',4)],
                            }
        return False

    def back_change_state(self, cr, uid, ids, context = None):
        o_l_state_obj = self.pool.get("pos.order.line.state")
        for order_lint in self.browse(cr, uid, ids, context = context):
            o_l_seq = o_l_state_obj.search(cr, uid, [('sequence', '<', order_lint.order_line_state_id.sequence)])
            sequence = []
            sequence_data = []
            for state_seq in o_l_state_obj.browse(cr, uid, o_l_seq, context = context):
                sequence.append(state_seq.sequence)
                sequence_data.append({'id':state_seq.id, 'sequence': state_seq.sequence})
            if sequence and type(sequence) is list:
                sequence.sort()
                sequence.reverse()
                for s_d in sequence_data:
                    if(s_d.get('sequence') == sequence[0]):
                        if sequence.__len__() == 1:
                            self.write(cr, uid, order_lint.id, {'order_line_state_id':s_d.get('id')}, context = context )
                            return {
                                'name': _('Kitchen Screen'),
                                'view_type': 'kanban',
                                'view_mode': 'kanban,tree,form',
                                'res_model': 'pos.order.line',
                                'view_id': False,
                                'tag':'reload',
                                'type': 'ir.actions.act_window',
                                'context':context,
                                'domain':[('order_id.state', '=', 'draft'), ('order_line_state_id','!=',4)],
                            }
                        else:
                            self.write(cr, uid, order_lint.id, {'order_line_state_id':s_d.get('id')}, context = context )
                            return {
                                'name': _('Kitchen Screen'),
                                'view_type': 'kanban',
                                'view_mode': 'kanban,tree,form',
                                'res_model': 'pos.order.line',
                                'view_id': False,
                                'tag':'reload',
                                'type': 'ir.actions.act_window',
                                'context':context,
                                'domain':[('order_id.state', '=', 'draft'), ('order_line_state_id','!=',4)],
                            }
        return False

    def _get_state_id(self, cr, uid, ids, context = None):
        stage_ids = self.pool.get('pos.order.line.state').search(cr, uid, [], order='sequence', context=context)
        return stage_ids and stage_ids[0] or False
   
    _defaults = {
        'flag':False,
        'order_line_state_id': _get_state_id,
    }

class pin_code(osv.Model):
    _name = 'pin.code'

    _columns = {
        'name': fields.char('Name', size=32),
        'code': fields.char('Code', size=32),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
    }

    def pin_code(self, cr, uid, code, context = None):
        code = self.search(cr, uid, [('code', '=', code)])
        today_date = time.strftime("%Y-%m-%d")
        if code:
            for rec in self.browse(cr, uid, code, context = context):
                if today_date > rec.date_from and today_date < rec.date_to:
                    return True
                else:
                     return False
        return False

class waiting_queue(osv.osv):
    _name = "waiting.queue"

    _order = 'sequence'

    _columns = {
        'partner_id' : fields.many2one("res.partner", "Partner"),
        'no_of_person' : fields.integer('No. Of Person'),
        'Resrvation_date' : fields.datetime("Reservation Date", required=True),
        'state' : fields.selection([('waiting','Waiting'),('allow','Allowed'),('left','Left')], "State"),
        'sequence' : fields.char('Sequence', required=True, readonly=True),
        'table_ids' : fields.many2many('table.master', 'table_queue_rel', 'table_id', 'table_queue_id', 'Table Master', readonly=True),
    }

    _defaults = {
        'Resrvation_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        'state': 'waiting',
        'no_of_person' : 1,
        'sequence' : '/',
    }

    def create(self, cr, uid, vals, context=None):
        if not vals.get('sequence'):
            vals.update({'sequence': self.pool.get('ir.sequence').get(cr, uid, 'waiting.queue')})
        return super(waiting_queue, self).create(cr, uid, vals, context=context)

    def change_state_left(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'left'}, context=context)

class res_partner(osv.osv):

    _inherit = 'res.partner'
    
    def create_customer_from_pos(self, cr, uid,c_name, c_street, c_street2, c_city,c_zip, c_phone, context=None):
        idClient = self.create(cr, uid, {
            'name':c_name,
            'street':c_street or False,
            'street2':c_street2 or False,
            'city':c_city or False,
            'zip':c_zip or False,
            'phone':c_phone or False,
            'customer': True,
        }, context=context)
        return idClient
    
    def edit_customer_from_pos(self, cr, uid,id,c_name, c_street, c_street2, c_city,c_zip, c_phone,context=None):
        self.write(cr,uid,[int(id)],{'name':c_name,'zip':c_zip,'phone':c_phone,'city':c_city,'street':c_street,'street2':c_street2},context=context)
        return True

res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: