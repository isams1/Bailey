openerp.point_of_sale_table = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var module = instance.point_of_sale;
    var set_screen = false;
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    module.PosModel.prototype.models.push({
        model:  'product.product',
        fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code',  'is_customizable', 'property_ids','is_product_description','is_product_wait',
                 'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                 'product_tmpl_id','image_small',],
        domain: [['sale_ok','=',true],['available_in_pos','=',true]],
        context: function(self){ return { pricelist: self.pricelist.id }; },
        loaded: function(self, products){
            self.db.add_products(products);
            self.all_product = products;
        },
    },{
        model:  'res.partner',
        fields: ['name','street','state_id','city','vat','street2','country_id','phone','zip','mobile','email','ean13','property_product_pricelist','write_date'],
        domain: null,
        loaded: function(self,partners){
            self.partners = partners;
            self.db.add_partners(partners);
        },
    },{
        model:  'table.master',
        fields: ['name','code','users_ids', 'capacities', 'available_capacities','area_id',],
        domain:  function(self){ return [['state','=','available'],['area_id', '!=', false]]; },
        loaded: function(self, tables_data){
            var tables = [];
            _.each(tables_data, function(item) {
                for(us in item.users_ids){
                    if(item.users_ids[us] == self.session.uid){
                        tables.push([item.id, item.name, item.capacities, item.capacities, item.available_capacities]);
                    }
                }
            });
            //self.all_table = tables_data;
            self.table_list = tables;
            self.temp_table_list = tables;
        },
    },{
        model:  'table.master',
        fields: ['name','code','users_ids', 'capacities', 'available_capacities','area_id',],
        loaded: function(self, tables_data){
            self.all_table = tables_data;
        },
    },{
        model:  'area.area',
        fields: ['name','code','users_ids', 'capacities', 'available_capacities','area_id',],
        domain:  null,
        loaded: function(self, areas){
            self.areas = areas;
        },
    },{
        model: 'pos.config',
        fields: [],
        domain: function(self){ return [['id','=', self.pos_session.config_id[0]]]; },
        loaded: function(self,configs){
            self.config = configs[0];
            self.config.use_proxy = self.config.iface_payment_terminal || 
                                    self.config.iface_electronic_scale ||
                                    self.config.iface_print_via_proxy  ||
                                    self.config.iface_scan_via_proxy   ||
                                    self.config.iface_cashdrawer;
            self.config.customer_receipt = !!self.config.customer_receipt;
            self.config.pincode = !!self.config.pincode;

            self.barcode_reader.add_barcode_patterns({
                'product':  self.config.barcode_product,
                'cashier':  self.config.barcode_cashier,
                'client':   self.config.barcode_customer,
                'weight':   self.config.barcode_weight,
                'discount': self.config.barcode_discount,
                'price':    self.config.barcode_price,
            });
        },
    },{
        model:  'res.users',
        fields: ['name','ean13','company_id'],
        domain:  null,
        loaded: function(self, user_list){
            self.delivery_boy = [];
            _.each(user_list,function(user){
                self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
                self.pos_order_dataset.call("check_group_pos_delivery_boy",[user.id]).then(function(callback){
                    if(callback){
                        self.delivery_boy.push(user);
                    }
                 });
            });
            self.user_list = user_list;
        },
    },{
        model:  'product.pricelist',
        fields: ['name', 'id','currency_id'],
        domain:  null,
        loaded: function(self, pricelists){
            self.pricelists = pricelists;
        },
    },{
        model:  'product.property',
        fields: ['name','product_attribute_ids', 'single_choice'],
        domain:  null,
        loaded: function(self, property){
            self.property = property;
        },
    },{
        model:  'product.description',
        fields: ['name',],
        domain:  null,
        loaded: function(self, desc){
            self.gen_product_description = desc;
        },
    },{
        model:  'res.currency',
        fields: ['id','symbol','position','rounding','accuracy'],
        domain:  null,
        loaded: function(self, currencies){
            self.all_currency = currencies;
            _.each(currencies,function(currency){
                if(currency.id == self.pricelist.currency_id[0]){
                    self.currency = currency;
                }
            });
            if (self.currency.rounding > 0) {
                self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
            } else {
                self.currency.decimals = 0;
            }
        },
    });

    module.PosModel.prototype.load_new_partners = function(){
        var self = this;
        var def  = new $.Deferred();
        var fields;
        _.each( module.PosModel.prototype.models,function(model){
            if(model.model === 'res.partner'){
                fields = model.fields;
            }
        });
        new instance.web.Model('res.partner')
            .query(fields)
            .filter([['write_date','>',this.db.get_partner_write_date()]])
            .all({'timeout':3000, 'shadow': true})
            .then(function(partners){
                if (self.db.add_partners(partners)) {// check if the partners we got were real updates
                    def.resolve();
                }else {
                    def.reject();
                }
            }, function(){ def.reject(); });
        return def;
    },

    module.PosModel = module.PosModel.extend({
        add_new_order: function(callable){
            var self = this;
            self.callable = callable;
            var order = new module.Order({pos:this});
            this.set('selectedOrder', order);
            $(".order_screen").remove();
            $(".order_screen_content").remove();
            this.order_screen = new module.OrderScreenWidget(this, {});
            this.order_screen.appendTo($('.screens'));
            
            if(this.config.manage_delivery){
                self.selectOrderTypeDialog(false);
                self.pos_widget.screen_selector.set_current_screen('dialog');
            }
            else{
                $(".order_dialog").remove();
                if(! $('.orders')[0].childNodes.length){
                    self.openDialog(this.callable, false);
                    self.pos_widget.screen_selector.set_current_screen('dialog');
                }
                else{
                    self.openDialog(false, false);
                    self.pos_widget.screen_selector.set_current_screen('dialog');
                }
            }
        },

        delete_current_order: function(){
            var self = this;
            if(self.get('selectedOrder').attributes.id){
                self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
                self.pos_order_dataset.call("close_order", [[self.get('selectedOrder').attributes.id]]).done(function(callback){
                    if(callback){
                        self.get('selectedOrder').destroy({'reason':'abandon'});
                        if(self.get('orders').last()){
                            self.set({ selectedOrder: self.get('orders').last() });
                        }
                    }else if(! callback){
                        alert(_t("Can not remove order."));
                    }
                });
            }else{
                var self = this;
                var data = this.get('selectedOrder').attributes.table_data;
                self.table_master_dataset = new instance.web.DataSetSearch(self, 'table.master', {}, [] );
                self.table_master_dataset.read_slice(['id', 'name', 'capacities', 'available_capacities', "users_ids","area_id"]).then(function(table_records){
                    _.each(data,function(table_data){
                        _.each(table_records,function(table){
                            if(table_data.table_id == table.id){
                                if((table.available_capacities - table_data.reserver_seat) == 0){
                                    self.table_master_dataset.write(table_data.table_id,{'state': 'available','available_capacities':table.available_capacities - table_data.reserver_seat  });
                                }else{
                                    self.table_master_dataset.write(table_data.table_id,{'state': 'available','available_capacities': table.available_capacities - table_data.reserver_seat });
                                }
                            }
                        });
                    });
                });
                this.get('selectedOrder').destroy({'reason':'abandon'});
            }
        },

        on_removed_order: function(removed_order,index,reason){
            var self = this;
            if( (reason === 'abandon' || removed_order.temporary || this.get('orders').last()) && this.get('orders').size() > 0){
                // when we intentionally remove an unfinished order, and there is another existing one
                self.kitchen_receipt = self.get('orders').last().kitchen_receipt;
                self.customer_receipt = self.get('orders').last().customer_receipt;
                _.each(self.pricelists,function(pricelist){
                    if(pricelist.id == self.get('orders').last().attributes.pricelist_id){
                        $("#pricelist_selection").val(pricelist.id + '-' + pricelist.name + '-'+ pricelist.currency_id[0]);
                        self.current_pricelist = pricelist.id;
                        var default_currency = true;
                        _.each(self.all_currency,function(currency){
                            if(currency.id == pricelist.currency_id[0]){
                                self.currency['id'] = currency.id;
                                self.currency['symbol'] = currency.symbol;
                                self.currency['position'] = currency.position;
                                default_currency = false;
                            }
                        });
                        if(default_currency){
                            self.currency['id'] = self.currency_temp_id;
                            self.currency['symbol'] = self.currency_temp_symbol;
                            self.currency['position'] = self.currency_temp_position;
                        }
                    }
                });
                this.set({'selectedOrder' : this.get('orders').at(index) || this.get('orders').last()});
            }else{
                // when the order was automatically removed after completion,
                // or when we intentionally delete the only concurrent order
                this.add_new_order();
            }
        },

        selectOrderTypeDialog: function(callable){
            var self = this;
            self.callable = callable;
            var available_customer = [];
            var customer_details = [];
            var available_user = [];
            _.each(self.partners, function(partner) {
                available_customer.push(partner.name);
                customer_details.push(partner);
            });
            _.each(self.delivery_boy,function(user){
                available_user.push(user.name);
            });
            $('#input_delivery_boy').live('keypress', function(e){
                $("#input_delivery_boy").autocomplete({
                    source: available_user,
                });
                $('.ui-autocomplete-input').css('fontSize', '25px');
                $('.ui-autocomplete').addClass('openerp');
                $('ui-menu-item').css('text-align','left');
                $('ui-menu-item').css('font-size','25px');
                $('.ui-helper-hidden-accessible').css('display','none');
                $('.ui-autocomplete').css({"height":"60px","width":'60px','border':'1px solid gray','list-style':'none','text-align':'left','overflow-y':'auto','position':'fixed','background':'silver','top':'290px'});
            });
            $('#input_customer').live('keyup',function(e){
                $("#person_number_txt").val("");
            });
            $('#input_customer').live('keypress', function(e){
                $("#input_customer").autocomplete({
                    source: available_customer,
                    response: function (event, ui) {
                        this.text_customer = $("#input_customer").val();
                        var ui_length = 0;
                        for (ui_obj in ui.content){
                            ui_length++;
                        }
                        ui.content.push({
                            label:  _.str.sprintf(('Create and Edit...'),
                                $('<span id="create_and_edit"/>').text(this.text_customer).html()),
                                button: true
                        });
                    },
                    select: function (event, ui) {
                        if($(ui)[0].item.value){
                            selected_partner = $(ui)[0].item.value.split('] ')[1];
                            if(! selected_partner){
                                selected_partner = $(ui)[0].item.value;
                            }
                        }
                        create_partner = $(ui)[0].item.label.split(" ")[0];
                        if($(ui)[0].item.label == "Create and Edit..."){
                            var edit_status = false;
                            var customer_id = 0;
                            self.add_customer_dialog = $(QWeb.render('add-customer', {'widget': self})).dialog({
                                resizable: false,
                                height:415,
                                width:400,
                                title: _t("Add Customer"),
                                position: "center",
                                modal : true,
                                close: function( event, ui ) {
                                    $( this ).remove();
                                },
                                buttons: {
                                    "Ok": function() {
                                        var c_name = ($("#customer_name").val()).trim();
                                        var c_street = ($("#input_street").val()).trim();
                                        var c_street2 = ($("#input_street2").val()).trim();
                                        var c_city = ($("#input_city").val()).trim();
                                        var c_zip = ($('#input_zip').val()).trim();
                                        var c_phone = ($('#input_phone').val()).trim();
                                        var nb_error = 0;
                                        if(edit_status){
                                            if (c_name == ''){
                                                alert(_t("Please Enter Customer Name."));
                                                nb_error++;
                                                return false;
                                            }
                                            var Partners = new instance.web.Model('res.partner');
                                            Partners.call('edit_customer_from_pos', [customer_id,c_name, c_street,c_street2,c_city,c_zip, c_phone])
                                                .done(function(){
                                                    (new instance.web.Model('res.partner')).get_func('read')(customer_id).then(function(callback){
                                                        $("#input_customer").val(callback.name);
                                                        $("#person_number_txt").val(callback.phone);
                                                        customer_details.push(callback);
                                                    });
                                                });
                                            $( this ).remove();
                                            self.add_customer_dialog.remove();
                                        }
                                        if(! edit_status){
                                            if (c_name == ''){
                                                alert("Please Enter Customer Name.");
                                                nb_error++;
                                                return false;
                                            }
                                            if (c_phone == ''){
                                                alert("Please Enter Customer Phone Number.");
                                                nb_error++;
                                                return false;
                                            }
                                            if (nb_error > 0){
                                                alert(_t("Please Enter Correct Data"));
                                            }else{
                                                var Partners = new instance.web.Model('res.partner');
                                                Partners.call('create_customer_from_pos', [c_name, c_street,c_street2,c_city,c_zip, c_phone])
                                                    .fail(function(clientId){
                                                        alert(_t('Error : Can not create customer'));
                                                    }).done(function(clientId){
                                                          (new instance.web.Model('res.partner')).get_func('read')(clientId).then(function(callback){
                                                              $("#input_customer").val(callback.name);
                                                              available_customer.push(callback.name);
                                                              self.partners.push(callback);
                                                              self.partner_list.push(callback);
                                                              $("#person_number_txt").val(callback.phone);
                                                              customer_details.push(callback);
                                                          });
                                                    });
                                                    $( this ).remove();
                                                    self.add_customer_dialog.remove();
                                            }
                                        }
                                    },
                                    "Close": function() {
                                        $( this ).remove();
                                        self.add_customer_dialog.remove();
                                    }
                                },
                            });
                            $("#customer_name").val($("#input_customer")[0].text_customer);
                            _.each(customer_details,function(partner){
                                if(partner.name == $("#customer_name").val()){
                                    edit_status = true;
                                    customer_id = partner.id;
                                    $("#input_street").val(partner.street);
                                    $("#input_city").val(partner.city);
                                    $('#input_zip').val(partner.zip);
                                    $('#input_phone').val(partner.phone);
                                    $('#input_street2').val(partner.street2);
                                }
                            });
                            $("#customer_name").val($("#input_customer")[0].text_customer);
                        }else if(create_partner == "Create"){
                            res_partner_dataset = new instance.web.DataSetSearch(self, 'res.partner', {}, [] );
                            $("#input_customer").val(this.text_customer);
                            new instance.web.DataSet(self, 'res.partner', [])
                                .name_create(this.text_customer).done(function(data) {
                                    add_partner = {
                                        name:data[1],
                                        id:data[0],
                                        ean13: false,
                                    };
                                    self.load_new_partners(),data[1];
                                    available_customer.push(data[1]);
                                    customer_details.push(data);
                                });
                        }
                        if (ui.item.button) {
                            event.preventDefault();
                        }
                    }
                });
                $('.ui-autocomplete').addClass('openerp');
                $('ui-menu-item').css('text-align','left');
                $('.ui-helper-hidden-accessible').css('display','none');
                $('.ui-autocomplete').css({"font-weight": "normal","font-size":"12px","height":"300px","width":'60px','border':'1px solid gray','list-style':'none','text-align':'left','overflow':'auto','position':'fixed','background':'silver','top':'290px'});
            });
            self.dialog_event_handler = function(e){
                if(e.keyCode == 13){
                    $('#create').click();
                }
            };
            $('#dine_in').click(function(){
                self.openDialog(self.callable, false,true);
                $(".table_dialog").show();
                $(".table_content").hide();
            });
            $('#dine_in').click()
            $('#take_away').click(function(){
                self.openDialog(self.callable, false,false,true);
                $(".table_dialog").show();
                $(".table_content").hide();
            });
            $('#delivery_order').click(function(){
                self.openDialog(self.callable, false,false,false,true);
                $(".table_dialog").show();
                $(".table_content").hide();
            });
            $('#close_pos').click(function(){
                if (confirm(_t("Pending orders will be lost.\nAre you sure you want to leave this session?"))) {
                    return new instance.web.Model("ir.model.data").get_func("search_read")([['name', '=', 'action_client_pos_menu']], ['res_id']).pipe(function(res) {
                        window.location = '/web#action=' + res[0]['res_id'];
                    });
                }
            });
        },

        openDialog: function(callable, re_assign,dine_in,take_away,delivery){
            var self = this;
            self.callable = callable;
            $(".rightpane").css("border-left","1px solid #c7c7c7");
            self.booked_table = [];
            this.empty_table = [];
            self.waiter_list = [];
            self.partner_list = [];
            self.re_assign = re_assign;
            self.callable = callable;
            self.delivery = delivery;
            _.each(self.partners, function(value) {
                self.partner_list.push(value);
            });
            self.table_master_dataset = new instance.web.DataSetSearch(self, 'table.master', {}, []);
            self.table_master_dataset.call("get_waiter_list").then(function(waiter_list){
                _.each(waiter_list, function(value) {
                    self.waiter_list.push([value.id,value.name]);
                });
            });
            self.table_master_dataset.read_slice(['id', 'name', 'capacities', 'available_capacities', "users_ids","area_id"], {'domain': [['state', '=', 'available'],['area_id', '!=', false]]}).then(function(table_records){
                _.each(table_records, function(value) {
                    for(us in value.users_ids){
                        if(value.users_ids[us] == self.session.uid){
                            if((value.capacities - value.available_capacities) < value.capacities){
                                self.empty_table.push([value.id, value.name, value.capacities, value.capacities - value.available_capacities, value.available_capacities, true,value.area_id[0]]);
                            }else{
                                self.empty_table.push([value.id, value.name, value.capacities, value.capacities - value.available_capacities, value.available_capacities, false,value.area_id[0]]);
                            }
                        }
                    }
                });
                if ($('.orders')) {
                    _.each($('.orders')[0].childNodes, function(value) {
                        if($(value).attr('data')){
                            self.booked_table.push([$(value).attr("name"), $(value).text().trim(), $(value).attr("data")]);
                        }
                    });
                }
                if(re_assign && self.empty_table == "" && self.option_value == "re_assign_order"){
                    alert(_t("Table is not empty. Please wait!"));
                    return false;
                }
                if(self.booked_table.length < 0 && self.option_value == "merge_order"){
                    alert(_t("There is no more table to merge!"));
                    return false;
                }
                if(self.re_assign ){
                    $(".table_dialog").hide();
                    $(".table_content").remove();
                    $(".table_screen").append("<div class='table_content'></div>");
                    $(".table_content").append($(QWeb.render('select-table', {'table' : self})));
                    $(".table_content").append("<br/><button style='background:#DC5F59;color:white;margin:5px;height: 50px;width: 107px;' id='create'><b>"+self.option_text+"</b></button><button style='background:#359766;color:white;height: 50px;width: 60px;' id='back'><b>Back</b></button>");
                    $(".table_content").css("float","left");
                    $(".table_content").css("margin-left","1%");
                }else{
                    $(".table_content").remove();
                    $(".order_screen_content").remove();
                    $(".order_screen").append("<div class='order_screen_content' ></div>");
                    $(".order_screen_content").append($(QWeb.render('select-table', {'table' : self})));
                    $(".order_screen_content").append("<br/><br/><button style='background:#DC5F59;color:white;border: solid 1px #BEBEBE;display: inline-block;line-height: 38px;min-width: 38px;text-align: center;border-radius: 3px;padding: 0px 10px;font-size: 15px;cursor: pointer;' id='create'>Create</button>");
                    $(".order_screen_content").css("float","left");
                    $(".order_screen_content").css("margin-left","1%");
                }
                $("#take_away_txt").focus();
                $("#input_customer").focus();
                $('#back').click(function(){
                    $("#options").show();
                    var dialog = this;
                    if(self.attributes.orders.models[0]){
                        $(".neworder-button").removeAttr("disabled");
                        $(".oe_dropdown_toggle").css("display","block");
                        if(self.callable){
                            self.set('selectedOrder', self.get('orders').models[0]);
                            window.screen_selector = self.callable.screen_selector;
                            instance.webclient.set_content_full_screen(true);
                        }
                        $( dialog ).remove();
                    }else{
                        alert(_t("There is no other order are available. So please create order!"));
                        $( dialog ).remove();
                        if(self.config.manage_delivery){
                            self.selectOrderTypeDialog(self.callable);
                        }
                        else if(!self.config.manage_delivery) {
                            self.openDialog(self.callable, false, false, false, false);
                        }
                    }
                    var previous = self.get('selectedOrder').get_screen_data('previous-screen');
                    self.pos_widget.screen_selector.set_current_screen(previous);
                });
                $("#create").click(function(){
                    selection_name= '';
                    selection_id = [];
                    flag = true;
                    reserved_seat = '';
                    $(".neworder-button1").show();
                    $(".deleteorder-button").show();
                    select_tables = [];
                    self.is_any_checked_table = false;
                    $(".oe_dropdown_toggle").css("display","block");
                    $(".neworder-button").removeAttr("disabled");
                    $('#table_list tr input[type="checkbox"]:checked').each(function(index){
                        self.is_any_checked_table = true;
                        selection_name += ' ' + this.value +"/" + $("#"+$(this).attr('id')+'_reserv_sit').val();  //selected_row[1]
                        table_id = parseInt($(this).attr('id'));
                        selection_id.push(table_id); //selected_row[0]
                        reserved_seat += $(this).attr('id')+ "/" +$("#"+$(this).attr('id')+'_reserv_sit').val()+'_';
                        actual_reserved_seat = parseInt($("#"+$(this).attr('id')+'_reserv_sit').val());
                        already_booked_seat = parseInt($("#"+$(this).attr('id')+'_reserv_sit').attr('booked'));
                        available_seat = parseInt($("#"+$(this).attr('id')+'_leaft_seat')[0].innerHTML);
                        select_tables.push({reserver_seat: $("#"+$(this).attr('id')+'_reserv_sit').val(), table_id: table_id});
                        var table_vals = {'available_capacities': actual_reserved_seat + already_booked_seat};
                        if (actual_reserved_seat == available_seat) {
                            table_vals['state'] = 'reserved';
                        }
                        if(self.re_assign){
                            if($("#booked_table option:selected").val()){
                                self.table_master_dataset.write(table_id, table_vals);
                            }
                            else{
                                return false;
                            }
                        }else{
                            self.table_master_dataset.write(table_id, table_vals);
                        }
                        if (actual_reserved_seat <= 0) {
                            alert(_t("You must be add some person in this table"));
                            flag = false;
                        }
                        if((actual_reserved_seat >  available_seat) || (available_seat == 0) ){
                            alert(_t("Table capacity is ") + $("#"+$(this).attr('id')+'_leaft_seat')[0].innerHTML + _t(" person you cannot enter more then ") + $("#"+$(this).attr('id')+'_leaft_seat')[0].innerHTML + _t(" or less than 1. "));
                            flag = false;
                        }
                        this.checked = false;
                    });
                    if(! self.re_assign && ! self.delivery){
                        if(flag){
                            if($(".chk_take_away").is(":checked")){
                                iptxtval = $("#take_away_txt").val();
                                var order = new module.Order({ pos: self });
                                pflag = true;
                                partner_id = false;
                                driver_name = false;
                                phone = false;
                                order.set('creationDate',iptxtval);
                                order.set('creationDateId', iptxtval);
                                order.set('pflag',pflag);
                                order.set('parcel',iptxtval);
                                order.set('partner_id',partner_id);
                                order.set('driver_name',driver_name);
                                order.set('phone',phone);
                                if(iptxtval.length == 0 ){
                                    alert(_t("Parcel Order is Empty,Please Enter Parcel Order Name"));
                                    return false;
                                }else if (self.callable){
                                    self.get('orders').add(order);
                                    self.set('selectedOrder', order);
                                    self.callable.build_widgets();
                                    self.callable.screen_selector.set_current_screen('products');
                                    $(".order_screen_content").remove();
                                    window.screen_selector = self.callable.screen_selector;
                                    instance.webclient.set_content_full_screen(true);
                                    if (!self.pos_session) {
                                        self.callable.screen_selector.show_popup('error', 'Sorry, we could not create a user session');
                                    }else if(!self.config){
                                        self.callable.screen_selector.show_popup('error', _t('Sorry, we could not find any PoS Configuration for this session'));
                                    }
                                    $(this).remove();
                                }else{
                                      self.get('orders').add(order);
                                      self.set('selectedOrder', order);
                                      self.pos_widget.screen_selector.set_current_screen('products');
                                      $(".order_screen_content").remove();
                                }
                            }else if(selection_name && selection_id && selection_id && reserved_seat){
                                var order = new module.Order({ pos: self });
                                order.set('creationDate', selection_name);
                                order.set('creationDateId', selection_id);
                                order.set('table_ids', selection_id);
                                order.set('reserved_seat', reserved_seat);
                                order.set('table_data', select_tables);
                                if (self.callable){
                                    self.get('orders').add(order);
                                    self.callable.build_widgets();
                                    self.callable.screen_selector.set_current_screen('products');
                                    $(".order_screen_content").remove();
                                    window.screen_selector = self.callable.screen_selector;
                                    instance.webclient.set_content_full_screen(true);
                                    if (!self.pos_session) {
                                        self.callable.screen_selector.show_popup('error', _t('Sorry, we could not create a user session'));
                                    }else if(!self.config){
                                        self.callable.screen_selector.show_popup('error', _t('Sorry, we could not find any PoS Configuration for this session'));
                                    }
                                }else{
                                    self.get('orders').add(order);
                                   self.set('selectedOrder', order);
                                   self.pos_widget.screen_selector.set_current_screen('products');
                                   $(".order_screen_content").remove();
                                }
                                $(this).remove();
                            }else{
                                alert(_t("Please select table , without table user can not make order"));
                                return false;
                            }
                        }
                    }else if(self.re_assign && ! self.delivery){
                        var dialog = this;
                        self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
                        booked_selected_table = $("#booked_table option:selected").val();
                        booked_selected_table = booked_selected_table.toString().replace('_,','_');
                        if(booked_selected_table){
                            if(self.option_value == "re_assign_order" && ! self.is_any_checked_table){
                                alert(_t("Please select table , without table user can not make order"));
                                return false;
                            }
                            var items = $("#booked_table option:selected").map(function() {
                                return $(this).text();
                            }).get();
                            items.join();
                            //if(selection_id != '' && reserved_seat){
                            _.each(self.attributes.orders.models, function(order){
                                if(($("#booked_table option:selected").val() == order.attributes.reserved_seat) &&  ! order.attributes.pflag && ! $(".marge_table").is(":checked")){
                                    self.pos_order_dataset.call('reassign_table', [booked_selected_table]);
                                    _.each(order.attributes.table_ids, function(id){
                                        self.table_master_dataset.write(id, {"state":"available"});
                                    });
                                    $("#"+order.attributes.name.replace(' ', '_')).attr("name", selection_id);
                                    $("#"+order.attributes.name.replace(' ', '_')).attr("data", reserved_seat);
                                    $("#"+order.attributes.name.replace(' ', '_')).text(selection_name);
                                    order.attributes.reserved_seat = reserved_seat;
                                    order.attributes.creationDate = selection_name;
                                    order.attributes.table_ids = selection_id;
                                    order.attributes.table_data =select_tables;
                                    self.pos_order_dataset.call("create_from_ui", [[order.export_as_JSON()], true,false]).then(function(order_id){
                                        self.attributes.selectedOrder.attributes.id = order_id[0];
                                        self.pos_widget.synchronize_order(false);
                                        setTimeout(function(){
                                            for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                self.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = false;
                                                self.attributes.selectedOrder.attributes.orderLines.models[idx].flag = false;
                                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                                for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                    if(self.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.attributes.selectedOrder.attributes.reserved_seat){
                                                        self.attributes.selectedOrder.attributes.orderLines.remove(self.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                                    }
                                                }
                                            }
                                        },300);
                                    });
                                    $(".table_content").hide();
                                    self.pos_widget.screen_selector.set_current_screen('products');
                                }else if(self.option_value == "merge_order"){
//                                  self.option_value = ''
                                    var table_name = (items.toString().replace(',',' ') +selection_name).trim();
                                    table_name += ' ';
                                    if(booked_selected_table == order.attributes.reserved_seat){
                                        if(selection_name){
                                            $("#"+order.attributes.name.replace(' ', '_')).attr("data", order.attributes.reserved_seat +reserved_seat);
                                            $("#"+order.attributes.name.replace(' ', '_')).text(table_name);
                                            order.attributes.creationDate = table_name;
                                            order.attributes.reserved_seat = order.attributes.reserved_seat +reserved_seat;
                                            _.each(selection_id, function(id){
                                                order.attributes.table_ids.push(id);
                                            });
                                            _.each(select_tables, function(data){
                                                order.attributes.table_data.push(data);
                                            });
                                            $("#"+order.attributes.name.replace(' ', '_')).attr("name",  order.attributes.table_ids);
                                            self.set('selectedOrder', order);
                                            self.pos_order_dataset.call("create_from_ui", [[order.export_as_JSON()], true,false]).then(function(order_id){
                                                self.attributes.selectedOrder.attributes.id = order_id[0];
                                                self.pos_widget.synchronize_order(false);
                                                setTimeout(function(){
                                                    for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                        self.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = false;
                                                        self.attributes.selectedOrder.attributes.orderLines.models[idx].flag = false;
                                                        self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                                        for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                            if(self.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.attributes.selectedOrder.attributes.reserved_seat){
                                                                self.attributes.selectedOrder.attributes.orderLines.remove(self.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                                            }
                                                        }
                                                    }
                                                },300);
                                            });
                                        }
                                        _.each(self.get('orders').models, function(second_order){ 
                                            second_order.attributes.state = 'draft';
                                            if(order.attributes.user_id == second_order.attributes.user_id){
                                                if((table_name).search(second_order.attributes.creationDate) != -1){
                                                    if(second_order.partner_id && order.partner_id && (order.partner_id != second_order.partner_id)){
                                                        alert(_t("Partner are not same! So can not Merge table!"));
                                                        return false;
                                                    }else if(second_order.pricelist_id && order.pricelist_id && (second_order.pricelist_id != order.pricelist_id)){
                                                        alert(_t("Pricelist are not same! So can not Marge table!"));
                                                        return false;
                                                    }else if(second_order.user_id && order.user_id && (second_order.user_id != order.user_id)){
                                                        alert(_t("Salesman are not same! So can not Merge table!"));
                                                        return false;
                                                    }else{
                                                        if(second_order.attributes.name != order.attributes.name){
                                                            if(second_order.attributes.id && order.attributes.id){
                                                                self.pos_order_dataset.call("remove_order", [[order.attributes.id], second_order.attributes.id]).then(function(callback){
                                                                    if(callback){
                                                                        order.get('orderLines').add(second_order.attributes.orderLines.models);
                                                                        $("#"+order.attributes.name.replace(' ', '_')).attr("data", order.attributes.reserved_seat +second_order.attributes.reserved_seat);
                                                                        $("#"+order.attributes.name.replace(' ', '_')).text(table_name);
                                                                        _.each(second_order.attributes.table_ids, function(id){
                                                                            order.attributes.table_ids.push(id);
                                                                        });
                                                                        order.attributes.reserved_seat = order.attributes.reserved_seat + second_order.attributes.reserved_seat;
                                                                        order.attributes.creationDate = table_name;
                                                                        $("#"+order.attributes.name.replace(' ', '_')).attr("name", table_name);
                                                                        _.each(second_order.attributes.table_data, function(data){
                                                                            order.attributes.table_data.push(data);
                                                                        });
                                                                        self.set('selectedOrder', order);
                                                                        self.pos_order_dataset.call("create_from_ui", [[order.export_as_JSON()], true,false]).then(function(order_id){
                                                                            self.attributes.selectedOrder.attributes.id = order_id[0];
                                                                            self.pos_widget.synchronize_order(false);
                                                                            setTimeout(function(){
                                                                                for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                                   self.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = true;
                                                                                   for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                                       self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                                                                       if(self.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.attributes.selectedOrder.attributes.reserved_seat){
                                                                                           self.attributes.selectedOrder.attributes.orderLines.remove(self.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                                                                       }
                                                                                   }
                                                                                }
                                                                            },300);
                                                                        });
                                                                        second_order.destroy();
                                                                       // new instance.web.DataSet(this, 'pos.order').unlink([second_order.attributes.id]);
                                                                    }
                                                                    $(".table_content").hide();
//                                                                  $(dialog).remove()
                                                                });
                                                            }else if(second_order.attributes.id && ! order.attributes.id){
                                                                second_order.get('orderLines').add(order.attributes.orderLines.models);
                                                                $("#"+second_order.attributes.name.replace(' ', '_')).attr("data", second_order.attributes.reserved_seat +order.attributes.reserved_seat);
                                                                $("#"+second_order.attributes.name.replace(' ', '_')).text(table_name);
                                                                _.each(order.attributes.table_ids, function(id){
                                                                    second_order.attributes.table_ids.push(id);
                                                                });
                                                                second_order.attributes.creationDate = table_name; 
                                                                second_order.attributes.reserved_seat = second_order.attributes.reserved_seat + order.attributes.reserved_seat;
                                                                $("#"+second_order.attributes.name.replace(' ', '_')).attr("name", second_order.attributes.table_ids);
                                                                _.each(order.attributes.table_data, function(data){
                                                                    second_order.attributes.table_data.push(data);
                                                                });
                                                                self.set('selectedOrder', second_order);
                                                                self.pos_order_dataset.call("create_from_ui", [[second_order.export_as_JSON()], true,false]).then(function(order_id){
                                                                    self.attributes.selectedOrder.attributes.id = order_id[0]
                                                                    self.pos_widget.synchronize_order(false)
                                                                    setTimeout(function(){
                                                                        for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                            self.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = false;
                                                                            self.attributes.selectedOrder.attributes.orderLines.models[idx].flag = false;
                                                                            self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                                                            for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                                if(self.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.attributes.selectedOrder.attributes.reserved_seat){
                                                                                    self.attributes.selectedOrder.attributes.orderLines.remove(self.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                                                                }
                                                                            }
                                                                        }
                                                                    },300);
                                                                });
                                                                order.destroy();
                                                                $(".table_content").hide();
//                                                              $(dialog).remove()
                                                            }else {
                                                                order.get('orderLines').add(second_order.attributes.orderLines.models);
                                                                $("#"+order.attributes.name.replace(' ', '_')).attr("data", order.attributes.reserved_seat +second_order.attributes.reserved_seat);
                                                                $("#"+order.attributes.name.replace(' ', '_')).text(table_name);
                                                                $("#"+order.attributes.name.replace(' ', '_')).attr("name", table_name);
                                                                order.attributes.creationDate = table_name;
                                                                _.each(second_order.attributes.table_ids, function(id){
                                                                    order.attributes.table_ids.push(id);
                                                                });
                                                                order.attributes.reserved_seat = order.attributes.reserved_seat + second_order.attributes.reserved_seat;
                                                                $("#"+order.attributes.name.replace(' ', '_')).attr("name", order.attributes.table_ids);
                                                                _.each(second_order.attributes.table_data, function(data){
                                                                    order.attributes.table_data.push(data);
                                                                });
                                                                order.attributes.pricelist_id = parseInt($('#pricelist_selection').val().split('-')[0]);
                                                                self.set('selectedOrder', order);
                                                                self.pos_order_dataset.call("create_from_ui", [[order.export_as_JSON()], true,false]).then(function(order_id){
                                                                    self.attributes.selectedOrder.attributes.id = order_id[0];
                                                                    self.pos_widget.synchronize_order(false);
                                                                    setTimeout(function(){
                                                                        for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                            self.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = true;
                                                                            self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                                                            for( idx in self.attributes.selectedOrder.attributes.orderLines.models){
                                                                                if(self.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.attributes.selectedOrder.attributes.reserved_seat){
                                                                                    self.attributes.selectedOrder.attributes.orderLines.remove(self.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                                                                }
                                                                            }
                                                                        }
                                                                    },300);
                                                                });
                                                                second_order.destroy();
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        });
                                    }
                                }
                                $(".table_content").hide();
                                self.pos_widget.screen_selector.set_current_screen('products');
                            });
                        }else if(self.option_value == "re_assign_waiter" && ! self.delivery){
                            $('#booked_table_list tr input[type="checkbox"]:checked').each(function(index){
                                table_id = $(this).attr('id');
                                table_name = $(this).attr('value');
                                waiter_id = $('#select_waiter').val();
                                _.each(self.get("orders").models, function(order){
                                    var flag = false;
    //                                table_name = table_name.split(" ")[0]
                                    if(table_name.trim(" ") == order.attributes.creationDate.trim(" ")){
                                        var flag2 = false;
                                        _.each(self.all_table, function(table){
                                            _.each(order.attributes.table_ids, function(id){
                                                if(id == table.id){
                                                    _.each(table.users_ids, function(u_id){
                                                        if(parseInt(waiter_id) == u_id)
                                                            flag2 = true;
                                                    });
                                                }
                                            });
                                        });
                                        if (flag2)
                                            flag = true;
                                    }
                                    if(flag){
                                        order.waiter_id = waiter_id;
                                        order.attributes.user_id = waiter_id;
                                        if(order.attributes.orderLines.models == ''){
                                            alert(_t('Can not create order which have no order line.'));
                                            return false;
                                        }else{
                                            self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
                                            self.pos_order_dataset.call("create_from_ui", [[order.export_as_JSON()], true,false]).then(function(order_id){
                                                order.destroy();
                                            });
                                        }
                                    }
                                });
                            });
                            $(dialog).remove();
                            $(".table_content").hide();
                            self.pos_widget.screen_selector.set_current_screen('products');
                        }else{
                            alert(_t("Please select table , without table user can not make order"));
                            return false;
                        }
                        $(dialog).remove();
                    } else if (self.delivery){
                        if(! $('#input_customer').val()){
                            alert(_t("Please select Person."));
                            return false;
                        }else if ($('#input_customer').val()){
                            partner_id = $('#input_customer').val();
                        }
                        if(!$("#person_number_txt").val()){
                            alert(_t("Please enter phone number."));
                            return false;
                        }
                        if(! $('#input_delivery_boy').val()){
                            alert(_t("Please select driver."));
                            return false;
                        }else{
                            var customer_not_exits = true;
                            _.each(self.partners,function(partner){
                                if($('#input_customer').val() == partner.name){
                                    customer_not_exits = false;
                                }
                            });
                            if(customer_not_exits){
                                alert(_t("Customer not Exists"));
                                return false;
                            }
                            var driver_not_exits = true;
                            _.each(self.delivery_boy,function(user){
                                if(user.name.toLowerCase() == $('#input_delivery_boy').val().toLowerCase()){
                                    driver = user.id;
                                    driver_not_exits = false;
                                }
                            });
                            if(driver_not_exits){
                                alert(_t("Invalid Driver"));
                                return false;
                            }
                            phone = $("#person_number_txt").val();
                            var order = new module.Order({ pos: self });
                            pflag = false;
                            parcel = false;
                            order.set('partner_id', partner_id);
                            order.set('creationDate',partner_id);
                            order.set('creationDateId', partner_id);
                            order.set('pflag',pflag);
                            order.set('parcel',parcel);
                            order.set('driver_name',driver);
                            order.set('phone',phone);
                            if(partner_id.length == 0 ){
                                alert(_t("Person name is Empty,Please Enter Person Name"));
                                return false;
                            }else if (self.callable){
                                self.get('orders').add(order);
                                self.set('selectedOrder', order);
                                self.callable.build_widgets();
                                self.callable.screen_selector.set_current_screen('products');
                                $(".order_screen_content").remove();
                                window.screen_selector = self.callable.screen_selector;
                                instance.webclient.set_content_full_screen(true);
                                if (!self.pos_session) {
                                    self.callable.screen_selector.show_popup('error', _t('Sorry, we could not create a user session'));
                                }else if(!self.config){
                                    self.callable.screen_selector.show_popup('error', _t('Sorry, we could not find any PoS Configuration for this session'));
                                }
                                $(this).remove();
                            }else{
                                _.each(self.partner_list, function(partner){
                                    if(order.attributes.partner_id == partner.name){
                                        order.attributes.phone = partner.phone;
                                        order.attributes.partner_id = partner.name;
                                    }
                                });
                                self.get('orders').add(order);
                                self.set('selectedOrder', order);
                                self.pos_widget.screen_selector.set_current_screen('products');
                                $(this).remove();
                            }
                            if(partner_id){
                                _.each(self.partners, function(partner) {
                                    if(partner.name == partner_id){
                                        self.get('selectedOrder').set_client(partner);
                                    }
                                });
                            }
                        }
                    }
                    $(".rightpane").css("border-left","0px solid #c7c7c7");
                    $(".pos-leftpane").show();
                });
                $("#select_waiter_lbl").hide();
                $("#select_waiter").hide();
                $("#booked_table_list").hide();
                $("#table_list").hide();
                if(self.config.show_area){
                    if( $("#area_table").val() != undefined){
                        $("#table_list tr").hide();
                        if($(".area_"+$("#area_table").val()).length > 0){
                            $(".area_"+$("#area_table").val()).show();
                            $("#table_list").show();
                        }else{
                            $("#parcel_order_lbl").hide();
                            $("#take_away_txt").hide();
                            $("#delivery_order_person_number").hide();
                            $("#person_number_txt").hide();
                            $("#add_driver").hide();
                            $("#take_away1").hide();
                            $(".chk_take_away").hide();
                            alert(_t("There is no table available for this Area."));
                            $("#table_list").hide();
                        }
                    }
                    $("#area_table").on('change', function() {
                        $("#table_list tr").hide();
                        if($(".area_"+this.value).length > 0){
                            $("#table_list").show();
                            $(".area_"+this.value).show();
                        }else{
                            alert(_t("There is no table available for this Area."));
                            $("#table_list").hide();
                        }
                    });
                }else{
                    var str = "Select Table";
                    $("#area_table_label" ).html(str.bold());;
                    $("#area_table").hide();
                    $("#table_list").show();
                }
                if(self.config.manage_delivery){
                     $(".chk_take_away").hide();
                     $("#take_away1").hide();
                }else{
                    $(".chk_take_away").show();
                    $("#take_away1").show();
                }
                $("#parcel_order_lbl").hide();
                $("#take_away_txt").hide();
                $("#delivery_order_person_number").hide();
                $("#person_number_txt").hide();
                $("#add_driver").hide();
                if(take_away){
                    $("#area_table_label" ).css("display","none");
                    $("#area_table" ).hide();
                    $( "#table_list" ).css("display","none");
                    $(".ui-dialog-title").text(_t("Parcel Order"));
                    $("#parcel_order_lbl").show();
                    $("#take_away_txt").show();
                    $(".chk_take_away").attr('checked', true);
                    $("#take_away_txt").show();
                    $("#parcel_order_lbl").show();
                    $("#delivery_order_person_number").hide();
                    $("#person_number_txt").hide();
                    $("#add_driver").hide();
                }else if(delivery){
                    $(".ui-dialog-title").text(_t("Delivery Order"));
                    $("#parcel_order_lbl").hide();
                    $("#take_away_txt").hide();
                    $("#delivery_order_person_number").show();
                    $("#person_number_txt").show();
                    $("#add_driver").show();
                    $( "#table_list" ).css("display","none");
                }
                if(re_assign){
                    $(".ui-dialog-title").text(self.option_text);
                    $(".marge_table").hide();
                    $(".chk_take_away").hide();
                    $("#take_away1").hide();
                    if(self.option_value == "merge_order"){
                        $("#select_waiter_lbl").hide();
                        $("#select_waiter").hide();
                        $("#booked_table_list").hide();
                        $( "#booked_table" ).attr( "multiple","multiple");
                        $(".marge_table").attr('checked', true);
                        $( "#booked_table" ).css({'margin-bottom':'-19px','height':'55px','background':'white'});
                        $( "#table_list" ).css("display","block");
                        $( "#table_list" ).css({'margin-top':'19px'});
                    }else{
                        $("#select_waiter_lbl").hide();
                        $("#select_waiter").hide();
                        $("#booked_table_list").hide();
                        $( "#table_list" ).css("display","block");
                        $(".marge_table").attr('checked', false);
                    }
                    if(self.option_value == "re_assign_waiter"){
                        $("#booked_table").hide();
                        $("#table_list").hide();
                        $("#booked_table_lbl").hide();
                        $("#select_waiter_lbl").show();
                        $("#select_waiter").show();
                        $("#booked_table_list").show();
                        $('#select_waiter option').each(function(){
                            if (this.value == self.attributes.uid) {
                                $(this).hide();
                            }
                        });
                    }
                }
                $(".ui-dialog-titlebar-close").click(function () {
                    $(".neworder-button").removeAttr("disabled");
                    $(".marge_table").hide();
                    $(".oe_dropdown_toggle").css("display","block");
                });
                $(".oe_dropdown_toggle").css("display","none");
                $(".neworder-button").attr("disabled","disabled");

                $('#chk_chk').click(function () {
                    if ($(this).attr('checked')) {
                        $("#table_list").hide();
                        $("#parcel_order_lbl").show();
                        $("#take_away_txt").show();
                        $("#select_waiter_lbl").hide();
                        $("#select_waiter").hide();
                        $("#area_table_label").hide();
                        $("#area_table").hide();
                    } else {
                        $("#area_table_label").show();
                        $("#area_table").val('');
                        $("#area_table").show();
                        $("#parcel_order_lbl").hide();
                        $("#take_away_txt").hide();
                    }
                });
                $('#person_number_txt').focus(function(){
                    _.each(self.partners, function(partner) {
                        if(partner.name.toLowerCase() == $('#input_customer').val().toLowerCase()){
                            if(!partner.phone){
                                $("#person_number_txt").val("");
                            }else{
                                $("#person_number_txt").val(partner.phone);
                            }
                        }
                    });
                });
            });
        },
    });

    module.Order = module.Order.extend({

        addProduct: function(product, descrip, price, description_ids, options){
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product, descrip: descrip, price: price, description_ids : description_ids});

            line.property_description = descrip;
            if (price){
                line.discription_price = price;
                line.price = line.price + price;
            }
//            self.pos_order_dataset.call("pole_display", [[product.display_name],[self.pos_widget.format_currency(parseFloat(line.price.toFixed(2)))],validate = false,false])
            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            var last_orderline = this.getLastOrderline();
            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                last_orderline.merge(line);
                this.pos_order_dataset = new instance.web.DataSetSearch(this, 'pos.order.line', {}, [] );
                this.pos_order_dataset.write(last_orderline.id,{'qty':  last_orderline.quantity,'discount':last_orderline.discount,'property_description':last_orderline.property_description});
            }else{
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
        },

        computeChanges: function(categories){
            var current = this.lineResume();
            var old     = this.old_resume || {};
            var json    = this.export_as_JSON();
            var add = [];
            var rem = [];

            for( product in current){
                if (typeof old[product] === 'undefined'){
                    add.push({
                        'id': product,
                        'name': this.pos.db.get_product_by_id(product).display_name,
                        'quantity': current[product],
                    });
                }else if( old[product] < current[product]){
                    add.push({
                        'id': product,
                        'name': this.pos.db.get_product_by_id(product).display_name,
                        'quantity': current[product] - old[product],
                    });
                }else if( old[product] > current[product]){
                    rem.push({
                        'id': product,
                        'name': this.pos.db.get_product_by_id(product).display_name,
                        'quantity': old[product] - current[product],
                    });
                }
            }

            for( product in old){
                if(typeof current[product] === 'undefined'){
                    rem.push({
                        'id': product,
                        'name': this.pos.db.get_product_by_id(product).display_name,
                        'quantity': old[product], 
                    });
                }
            }

            if(categories && categories.length > 0){
                // filter the added and removed orders to only contains
                // products that belong to one of the categories supplied as a parameter

                var self = this;
                function product_in_category(product_id){
                    var cat = self.pos.db.get_product_by_id(product_id).pos_categ_id[0];
                    while(cat){
                        for(var i = 0; i < categories.length; i++){
                            if(cat === categories[i]){
                                return true;
                            }
                        }
                        cat = self.pos.db.get_category_parent_id(cat);
                    }
                    return false;
                }

                var _add = [];
                var _rem = [];
                
                for(var i = 0; i < add.length; i++){
                    if(product_in_category(add[i].id)){
                        _add.push(add[i]);
                    }
                }
                add = _add;

                for(var i = 0; i < rem.length; i++){
                    if(product_in_category(rem[i].id)){
                        _rem.push(rem[i]);
                    }
                }
                rem = _rem;
            }

            return {
                'new': add,
                'cancelled': rem,
                'table': json.table || 'unknown table',
                'name': json.name  || 'unknown order',
            };
        },

        getUser: function() {
            return this.waiter_id ? this.waiter_id : $("#user_selection").val();
        },

        getDriver: function() {
            return this.get('driver_name');
        },

        getPartner: function() {
            var self = this;
            _.each(self.pos.partner_list,function(partner) {
                if(self.attributes.partner_id && self.attributes.partner_id == partner.name){
                    return partner.name;
                }else{
                    return false;
                }
            });
        },

        getphone: function() {
            if(this.get('phone')){
                return this.get('phone');
            }else{
                return false;
            }
        },

        getTotal: function() {
            return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax();
            }), 0);
        },

        getFlag: function() {
            return this.get('pflag');
        },

        getParcel: function() {
            return this.get('parcel');
        },

        getTable: function(){
            return this.get('table_data');
        },
        // the client related to the current order.
        set_client: function(client){
            var self = this;
            _.each(self.pos.partners, function(partner){
                if(partner.name == client.name){
                    price = partner.property_product_pricelist[0];
                    _.each(self.pos.pricelists,function(pricelist){
                        if (pricelist.id == price){
                            _.each(self.pos.all_currency,function(currency){
                                if(currency.id == pricelist.currency_id[0]){
                                    $("#pricelist_selection").val(pricelist.id + '-' + pricelist.name  + '-'+ pricelist.currency_id[0] );
                                    self.pos.currency['id'] = currency.id;
                                    self.pos.currency['symbol']=currency.symbol;
                                    self.pos.currency['position']=currency.position;
                                }
                            });
                        }
                    });
                    $('#pricelist_selection').change();
                }
            });
            this.set('client',client);
        },

        export_as_JSON : function() {
            var orderLines, paymentLines;
            orderLines = [];
            (this.get('orderLines')).each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            (this.get('paymentLines')).each(_.bind( function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            this.partner_id = 0;
            if(this.attributes.partner_id){
                for(partner in this.pos.partner_list){
                    if(this.pos.partner_list[partner].name == this.attributes.partner_id){
                        this.partner_id = this.pos.partner_list[partner].id;
                    }
                }
            }
            return {
                name: this.getName(),
                pflag:this.getFlag(),
                parcel: this.getParcel(),
                amount_paid: this.getPaidTotal(),
                amount_total: this.getTotal(),
                amount_tax: this.getTax(),
                amount_return: this.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos.pos_session.id,
                partner_id: this.get_client() ? this.get_client().id : null,
                phone: this.getphone(),
                pricelist_id:this.attributes.pricelist_id ? this.attributes.pricelist_id : null,
                driver_name: this.getDriver(),
                user_id: this.attributes.user_id ? this.attributes.user_id : this.getUser(),
                table_data: this.getTable(),
                id: this.attributes.id ? this.attributes.id : null,
                split_order: this.attributes.split ? this.attributes.split : null,
            };
        },
    });

    module.PosWidget.include ({
        start: function(){
            this.product_category_dataset = new instance.web.DataSetSearch(self, 'pos.category', {}, [] );
            this.product_pricelist_dataset = new instance.web.DataSetSearch(self, 'product.pricelist', {}, []);
            var self = this;
            return self.pos.ready.done(function() {
            // remove default webclient handlers that induce click delay

            $(document).off();
            $(window).off();
            $('html').off();
            $('body').off();
            $(self.$el).parent().off();
            $('document').off();
            $('.oe_web_client').off();
            $('.openerp_webclient_container').off();

            /* self.build_currency_template();*/
            self.pos.currency_temp_id = self.pos.currency['id'];
            self.pos.currency_temp_symbol = self.pos.currency['symbol'];
            self.pos.currency_temp_position = self.pos.currency['position'];
            self.renderElement();

            var flag = true;
            self.synchronize_order(false);
            self.$('.deleteorder-button').click(function(){
                if( !self.pos.get('selectedOrder').is_empty() ){
                    self.screen_selector.show_popup('confirm',{
                        message: _t('Destroy Current Order ?'),
                        comment: _t('You will lose any data associated with the current order'),
                        confirm: function(){
                            self.pos.delete_current_order();
                        },
                    });
                }else{
                    self.pos.delete_current_order();
                }
            });

            //when a new order is created, add an order button widget
            self.pos.get('orders').bind('add', function(new_order){
                var new_order_button = new module.OrderButtonWidget(null, {
                    order: new_order,
                    pos: self.pos
                });
                new_order_button.appendTo(this.$('.orders'));
                new_order_button.selectOrder();
            }, self);

            this.order_screen = new module.OrderScreenWidget(this, {});
            this.order_screen.appendTo($('.screens'));

            if(flag){
                if(self.pos.config.manage_delivery){
                    self.pos.selectOrderTypeDialog(self);
                }else{
                    $(".order_dialog").remove();
                    self.pos.openDialog(self, false);
                }
            }
            document.body.addEventListener('keyup',self.pos.dialog_event_handler);
            // self.build_widgets()
            $(".neworder-button1").hide();
            $(".deleteorder-button").hide();
            self.$('.neworder-button1').click(function(){
                self.pos.add_new_order(self);
                flag = false;
            });
            if(self.pos.config.iface_big_scrollbars){
                self.$el.addClass('big-scrollbars');
            }
            self.pos.barcode_reader.connect();

            instance.webclient.set_content_full_screen(true);

            self.$('.loader').animate({opacity:0},1500,'swing',function(){self.$('.loader').addClass('oe_hidden');});

//            self.pos.flush();

            }).fail(function(){   // error when loading models data from the backend
                return new instance.web.Model("ir.model.data").get_func("search_read")([['name', '=', 'action_pos_session_opening']], ['res_id'])
                    .pipe( _.bind(function(res){
                        return instance.session.rpc('/web/action/load', {'action_id': res[0]['res_id']})
                            .pipe(_.bind(function(result){
                                var action = result.result;
                                this.do_action(action);
                            }, this));
                    }, self));
            });
        },

        disable_rubberbanding: function(){
            // prevent the pos body from being scrollable. 
            document.body.addEventListener('touchmove',function(event){
                var node = event.target;
                while(node){
                    if(node.classList && node.classList.contains('touch-scrollable')){
                        return;
                    }
                    node = node.parentNode;
                }
                //event.preventDefault();
            });
        },

        synchronize_order: function(sync_order){
            var self = this;
            this.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
            this.pos_order_dataset.call("get_draft_state_order").then(function(callback){
                if(! callback.length && sync_order){
                    alert(_t("There is no Draft Order For user!"));
                    return false;
                }
                _.each(self.pos.attributes.orders.models, function(old_ord){
                    if(old_ord.attributes.id  ){ //&& old_ord.attributes.state
                        flag = true;
                        _.each(callback , function(back_ord){
                            if(back_ord.id == old_ord.attributes.id){
                                flag = false;
                            }
                        })
                        if(flag &&  old_ord.attributes.table_data  ){
                            old_ord.destroy();
                        }
                    }
                });
                _.each(callback,function(ord){
                    flag = true;
                    for(o in self.pos.attributes.orders.models){
                        if(self.pos.attributes.orders.models[o].attributes.name == ord.pos_reference){
                            flag = false;
                        }
                    }
                    if(flag){
                        // if order not in current orders than create a new order and add current orders
                        var order = new module.Order({pos: self.pos})
                        if(ord.partner_id){
                            _.each(self.pos.partners, function(partner) {
                                if(partner.name == ord.partner_id){
                                    order.set_client(partner);
                                }
                            })
                        }
                        order.attributes.creationDate =ord.table_name;
                        order.attributes.creationDateId = ord.table_ids;
                        order.attributes.table_ids = ord.table_ids;
                        order.attributes.name = ord.pos_reference;
                        order.attributes.partner_id = ord.partner_id;
                        order.attributes.id = ord.id;
                        order.attributes.reserved_seat = ord.reserved_seat;
                        order.attributes.table_data = ord.table_data;
                        order.attributes.state='draft';
                        order.attributes.user_id = ord.user_id;
                        order.attributes.pricelist_id = ord.pricelist_id;
                        $(".order_screen").remove();
                        $(".order_screen_content").remove();
                        if(ord.lines){
                            for(line in ord.lines){
                                products = self.pos.all_product;
                                for(p in products){
                                    if(products[p].id == ord.lines[line].product_id){
                                        product = products[p]
                                    }
                                }
                                var line_set = new module.Orderline({}, {pos: self.pos, order: order, product:product,price:ord.lines[line].price_unit});
                                line_set.quantity = ord.lines[line].qty;
                                line_set.set_quantity(ord.lines[line].qty);
                                line_set.price = ord.lines[line].price_unit;
                                line_set.set_unit_price(ord.lines[line].price_unit);
                                line_set.discount = ord.lines[line].discount;
                                line_set.set_discount(ord.lines[line].discount);
                                line_set.property_description = ord.lines[line].property_description;
                                line_set.set_property_desc(ord.lines[line].property_description);
                                line_set.flag = ord.lines[line].flag;
                                line_set.name = ord.lines[line].name;
                                line_set.id = ord.lines[line].id;
                                line_set.line_id = ord.lines[line].id;
                                line_set.wait = ord.lines[line].wait;
                                line_set.product=product;
                                order.get('orderLines').add(line_set);
                                if((ord.lines.length-1) == line){
                                    order.selected_orderline = line_set;
                                    order.selected_orderline.set_selected(false);
                                }
                            }
                        }
                        self.pos.get('orders').add(order);
                    }else{
                        set_screen = true;
                        //if order in current order than update order lines
                        _.each(self.pos.attributes.orders.models, function(order_get){
                            if(order_get.attributes.name == ord.pos_reference){
                                $("#"+order_get.attributes.name.replace(' ', '_')).attr("name", ord.table_name);
                                $("#"+order_get.attributes.name.replace(' ', '_')).attr("data", ord.reserved_seat);
                                if(ord.partner_id){
                                    $("#"+order_get.attributes.name.replace(' ', '_')).text(ord.partner_id +":"+ord.table_name);
                                    $("#"+order_get.attributes.name.replace(' ', '_')).prepend("<i class='fa fa-user'/>");
                                    if(order_get.attributes.client){
                                        if(ord.partner_id != order_get.attributes.client.name){
                                            _.each(self.pos.partners, function(partner) {
                                                if(partner.name == ord.partner_id){
                                                    order_get.set_client(partner);
                                                }
                                           })
                                        }
                                    }
                                    if(!order_get.attributes.client){
                                        _.each(self.pos.partners, function(partner) {
                                            if(partner.name == ord.partner_id){
                                                order_get.set_client(partner);
                                            }
                                        })
                                    }
                                }else{
                                    $("#"+order_get.attributes.name.replace(' ', '_')).text(ord.table_name );
                                    $("#"+order_get.attributes.name.replace(' ', '_')).prepend("<i class='fa fa-user'/>");
                                }
                                order_get.attributes.creationDate = ord.table_name;
                                order_get.attributes.creationDateId = ord.table_ids;
                                order_get.attributes.table_ids = ord.table_ids;
                                order_get.attributes.name = ord.pos_reference;
                                order_get.attributes.partner_id = ord.partner_id;
                                order_get.attributes.id = ord.id;
                                order_get.attributes.state = 'draft';
                                order_get.attributes.reserved_seat = ord.reserved_seat;
                                order_get.attributes.table_data = ord.table_data;
                                order_get.attributes.user_id = ord.user_id;
                                order_get.attributes.pricelist_id = ord.pricelist_id;
                                var order_line_ids = [];
                                order_line_ids = []
                                _.each(ord.lines, function(get_line){
                                    order_line_ids.push(get_line.id);
                                })
                                _.each(ord.lines, function(get_line){
                                    products = self.pos.all_product;
                                    for(p in products){
                                        if(products[p].id == get_line.product_id){
                                            product = products[p];
                                        }
                                    }
                                    var line_set = new module.Orderline({}, {pos: self.pos, order: order_get, product: product});
                                    line_set.id = get_line.id;
                                    line_set.line_id = get_line.id;
                                    line_set.flag = get_line.flag;
                                    line_set.quantity = get_line.qty;
                                    line_set.set_quantity(get_line.qty);
                                    line_set.price = get_line.price_unit;
                                    line_set.set_unit_price(get_line.price_unit);
                                    line_set.discount = get_line.discount;
                                    line_set.set_discount(get_line.discount);
                                    line_set.property_description = get_line.property_description;
                                    line_set.set_property_desc(get_line.property_description);
                                    _.each(order_get.get('orderLines').models,function(order_line,index){
                                        if( order_line_ids.indexOf(order_line.id) == -1 && order_line.id != undefined){
                                            order_get.get('orderLines').remove(order_get.get('orderLines').models[index]);
                                        }
                                        if(order_line.id == get_line.id){
                                            if(order_line.quantity != get_line.qty){
                                                order_get.get('orderLines').remove(order_get.get('orderLines').models[index]);
                                            }
                                        }
                                        if(order_line.id == get_line.id){
                                            if(order_line.price != get_line.price_unit){
                                                order_get.get('orderLines').remove(order_get.get('orderLines').models[index]);
                                            }
                                        }
                                        if(order_line.id == get_line.id){
                                            if(order_line.property_description != get_line.property_description){
                                                order_get.get('orderLines').remove(order_get.get('orderLines').models[index]);
                                            }
                                        }
                                        if(order_line.id == get_line.id){
                                            if(order_line.discount != get_line.discount){
                                                order_get.get('orderLines').remove(order_get.get('orderLines').models[index]);
                                            }
                                        }
                                    });
                                    order_get.get('orderLines').add(line_set);
                                });
                                order_get.attributes.partner_id = ord.partner_id ? ord.partner_id : '';
                                order_get.selectLine(order_get.getLastOrderline());
                            }
                        });
                    }
                    if(! set_screen && self.pos_widget.screen_selector == undefined){
                        self.pos_widget.build_widgets();
                        self.pos_widget.screen_selector.set_current_screen('products');
                        $(".neworder-button1").show();
                        $(".deleteorder-button").show();
                        set_screen = true;
                    }
                });
                if(sync_order){
                    alert(_t("Order synchronize Process has been Done!"));
                }
            })
        },

        add_categ_button: function(){
            var self = this;
            self.action_manager = new instance.web.ActionManager(self);
            _.each(self.pos.attributes.selectedOrder.attributes.orderLines.models, function(o_l){
                if(!o_l.ol_flag){
                    self.product_category_dataset.call("get_category_tree").then(function(category_tree){
                        _.each(category_tree,function(ctg){
                            if( _.contains(ctg.id, o_l.product.pos_categ_id[0])){
                                flag_ot = true;
                                for( idx in self.pos_widget.action_bar.button_list){
                                    if(self.pos_widget.action_bar.button_list[idx].label == _t(ctg.name)){
                                        flag_ot = false;
                                    }
                                }
                                if(flag_ot){
                                    self.pos_widget.action_bar.add_new_button({
                                        label: _t(ctg.name),
                                        icon: '/point_of_sale/static/src/img/icons/png48/printer.png',
                                        click: function() {
                                            var currentOrder = self.pos.get('selectedOrder');
                                            currentOrder.kitchen_receipt = true;
                                            currentOrder.customer_receipt = false;
                                            _.each((self.pos.get('selectedOrder')).get('orderLines').models, function(order_line){
                                                order_line.categ_name = _t(ctg.name);
                                                if( _.contains(ctg.id, order_line.product.pos_categ_id[0])){
                                                    order_line.product_name = order_line.product.display_name;
                                                    order_line.print_qty = order_line.quantity;
                                                    order_line.print = true;
                                                }else{
                                                    order_line.print = false;
                                                }
                                            });
                                            self.receipt_screen.refresh();
                                            self.pos_widget.screen_selector.set_current_screen('receipt');
                                            window.print();
                                        },
                                    });
                                }
                            }
                        });
                    });
                }
            });
        },

        change_user: function(value) {
            var self = this;
            self.pos.get("selectedOrder").attributes.user_id = value;
            self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
            self.pos_order_dataset.call("check_group_pos_cashier_user",[value]).then(function(callback){
                if(callback){
                    $(".paypad-button").show();
                    $("#order_confirm_button").hide();
                    if(! self.pos.config.pincode){
                        _.each(self.$el.find('button.mode-button'), function(button){
                            if($(button).data().mode != "quantity"){
                                $(button).removeAttr("disabled");
                            }
                        });
                    }
                }else{
                    $(".paypad-button").hide();
                    $("#order_confirm_button").show();
                    if(! self.pos.config.pincode){
                        _.each(self.$el.find('button.mode-button'), function(button){
                            if($(button).data().mode != "quantity"){
                                $(button).attr("disabled","disabled");
                            }
                        });
                    }
                }
            });
        },

        build_widgets : function(){
            var self = this;
            // --------  Screens ---------

            this.product_screen = new module.ProductScreenWidget(this,{});
            this.product_screen.appendTo(this.$('.screens'));

            this.order_screen = new module.OrderScreenWidget(this, {});
            this.order_screen.appendTo(self.$('.screens'));
            
            this.table_screen = new module.TableScreenWidget(this, {});
            this.table_screen.appendTo(this.$('.screens'));

            this.receipt_screen = new module.ReceiptScreenWidget(this, {});
            this.receipt_screen.appendTo(this.$('.screens'));

            this.payment_screen = new module.PaymentScreenWidget(this, {});
            this.payment_screen.appendTo(this.$('.screens'));

            this.clientlist_screen = new module.ClientListScreenWidget(this, {});
            this.clientlist_screen.appendTo(this.$('.screens'));

            this.scale_screen = new module.ScaleScreenWidget(this,{});
            this.scale_screen.appendTo(this.$('.screens'));


            // --------  Popups ---------

            this.error_popup = new module.ErrorPopupWidget(this, {});
            this.error_popup.appendTo(this.$el);

            this.error_barcode_popup = new module.ErrorBarcodePopupWidget(this, {});
            this.error_barcode_popup.appendTo(this.$el);

            this.error_traceback_popup = new module.ErrorTracebackPopupWidget(this,{});
            this.error_traceback_popup.appendTo(this.$el);

            this.confirm_popup = new module.ConfirmPopupWidget(this,{});
            this.confirm_popup.appendTo(this.$el);

            this.unsent_orders_popup = new module.UnsentOrdersPopupWidget(this,{});
            this.unsent_orders_popup.appendTo(this.$el);


            // --------  Misc ---------

            this.close_button = new module.HeaderButtonWidget(this,{
                label: _t('Close'),
                action: function(){ 
                    var self = this;
                    if (!this.confirmed) {
                        this.$el.addClass('confirm');
                        this.$el.text(_t('Confirm'));
                        this.confirmed = setTimeout(function(){
                            self.$el.removeClass('confirm');
                            self.$el.text(_t('Close'));
                            self.confirmed = false;
                        },2000);
                    } else {
                        clearTimeout(this.confirmed);
                        this.pos_widget.close();
                    }
                },
            });
            this.close_button.appendTo(this.$('.pos-rightheader'));

            this.notification = new module.SynchNotificationWidget(this,{});
            this.notification.appendTo(this.$('.pos-rightheader'));

            if(this.pos.config.use_proxy){
                this.proxy_status = new module.ProxyStatusWidget(this,{});
                this.proxy_status.appendTo(this.$('.pos-rightheader'));
            }

            this.username   = new module.UsernameWidget(this,{});
            this.username.replace(this.$('.placeholder-UsernameWidget'));

            this.action_bar = new module.ActionBarWidget(this);
            this.action_bar.replace(this.$(".placeholder-RightActionBar"));

            this.paypad = new module.PaypadWidget(this, {});
            this.paypad.replace(this.$('.placeholder-PaypadWidget'));

            this.numpad = new module.NumpadWidget(this);
            this.numpad.replace(this.$('.placeholder-NumpadWidget'));

            this.order_widget = new module.OrderWidget(this, {});
            this.order_widget.replace(this.$('.placeholder-OrderWidget'));

            this.onscreen_keyboard = new module.OnscreenKeyboardWidget(this, {
                'keyboard_model': 'simple'
            });
            this.onscreen_keyboard.replace(this.$('.placeholder-OnscreenKeyboardWidget'));

            // --------  Screen Selector ---------

            this.screen_selector = new module.ScreenSelector({
                pos: this.pos,
                screen_set:{
                    'products': this.product_screen,
                    'payment' : this.payment_screen,
                    'scale':    this.scale_screen,
                    'receipt' : this.receipt_screen,
                    'clientlist': this.clientlist_screen,
                    'dialog':this.order_screen,
                    'table_screen': this.table_screen,
                },
                popup_set:{
                    'error': this.error_popup,
                    'error-barcode': this.error_barcode_popup,
                    'error-traceback': this.error_traceback_popup,
                    'confirm': this.confirm_popup,
                    'unsent-orders': this.unsent_orders_popup,
                },
                default_screen: 'products',
                default_mode: 'cashier',
            });

            if(this.pos.debug){
                this.debug_widget = new module.DebugWidget(this);
                this.debug_widget.appendTo(this.$('.pos-content'));
            }

            this.disable_rubberbanding();
            self.change_user(self.pos.user.id);

            if(self.pos.config.iface_splitbill){
                self.splitbill_screen = new module.SplitbillScreenWidget(self,{});
                self.splitbill_screen.appendTo(self.$('.screens'));
                self.screen_selector.add_screen('splitbill',self.splitbill_screen);

                var splitbill = $(QWeb.render('SplitbillButton'));

                splitbill.click(function(){
                    if(self.pos.get('selectedOrder').attributes.id){
                        if(self.pos.get('selectedOrder').get('orderLines').models.length > 0){
                            self.pos_widget.screen_selector.set_current_screen('splitbill');
                        }
                    }
                });
                
                self.$('.control-buttons').find('.order-split').remove();
                splitbill.appendTo(self.$('.control-buttons'));
                self.$('.control-buttons').removeClass('oe_hidden');
            }

            if(self.pos.printers.length){
                var submitorder = $(QWeb.render('SubmitOrderButton'));

                submitorder.click(function(){
                    var order = self.pos.get('selectedOrder');
                    if(order.hasChangesToPrint()){
                        order.printChanges();
                        order.saveChanges();
                        self.pos_widget.order_widget.update_summary();
                    }
                });

                submitorder.appendTo(self.$('.control-buttons'));
                self.$('.control-buttons').removeClass('oe_hidden');
            }
            $('#send_to_kitchen').click(function(){
                if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                    alert(_t('Can not create order which have no order line.'));
                    return false;
                }else{
                    var currentOrder = self.pos.get('selectedOrder');
                    currentOrder.attributes.pricelist_id = parseInt($("#pricelist_selection" ).val().split('-')[0]);
                    
                    self.pos_order_dataset.call("create_from_ui", [[currentOrder.export_as_JSON()], true,false]).done(function(order_id){
                        self.pos.attributes.selectedOrder.attributes.id = order_id[0];
                        self.synchronize_order(false);
                        setTimeout(function(){
                            for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = true;
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].flag = true;
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                    if(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.pos.attributes.selectedOrder.attributes.reserved_seat){
                                         self.pos.attributes.selectedOrder.attributes.orderLines.remove(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                    }
                                }
                            }
                        },300);
                        setTimeout(function(){
                            alert('Order send to the kitchen successfully!');
                        },300);
                    });
                }
            });

            $('.paypad-button').click(function(){
                if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                    self.pos_widget.screen_selector.set_current_screen('products');
                    alert(_t('Can not create order which have no order line.'));
                    return false;
                }else{
                    self.pos.kitchen_receipt = false;
                    self.pos.customer_receipt = false;
                    $(".order_screen").remove();
                    var currentOrder = self.pos.get('selectedOrder');
                   // currentOrder.attributes.pricelist_id =  parseInt($("#pricelist_selection" ).val().split('-')[0])
                    currentOrder.kitchen_receipt = false;
                    currentOrder.customer_receipt = false;
                    self.pos_order_dataset.call("create_from_ui", [[currentOrder.export_as_JSON()], true,false]).then(function(order_id){
                        self.pos.attributes.selectedOrder.attributes.id = order_id[0];
                        self.synchronize_order(false);
                        setTimeout(function(){
                            for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = false;
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                    if(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.pos.attributes.selectedOrder.attributes.reserved_seat){
                                        self.pos.attributes.selectedOrder.attributes.orderLines.remove(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                    }
                                }
                            }
                        },300);
                    });
                }
            });

            if(! self.pos.get('selectedOrder').attributes.driver_name){
                _.each(self.pos.pricelists,function(pricelist){
                    if (pricelist.id == self.pos.pricelist.id){
                        $("#pricelist_selection").val(pricelist.id + '-' + pricelist.name  + '-'+ pricelist.currency_id[0] );
                        self.pos.current_pricelist = pricelist.id;
                    }
                });
                $('#pricelist_selection option[value=""]').remove();
            }

            $("#pricelist_selection" ).on( "change", function(attrs){
                var value = $(this).val();
                self.pos.current_pricelist = parseInt(value);
                self.pos.current_pricelist_id = value;
                if(self.pos.get('selectedOrder').get("orderLines").length){
                    _.each($("#pricelist_selection option"), function(att){
                        if(att.value == self.pos.current_pricelist_id){
                            att.selected = true;
                        }
                    });
                    _.each(self.pos.get('selectedOrder').get("orderLines").models, function(line){
                        self.product_pricelist_dataset.call("price_get" , [[self.pos.current_pricelist],line.product.id, line.quantity]).done(function(callback){
                            if(callback[parseInt(self.pos.current_pricelist)] != false ){
                                if(callback[parseInt(self.pos.current_pricelist)] < 0){
                                    price = callback[parseInt(self.pos.current_pricelist)] * -1;
                                    price += line.discription_price ?  line.discription_price : 0;
                                    line.set_unit_price(price);
                                }else{
                                    price = callback[parseInt(self.pos.current_pricelist)];
                                    price += line.discription_price ?  line.discription_price : 0;
                                    line.set_unit_price(price);
                                }
                            }
                        });
                    });
                }
                var default_currency = true;
                _.each(self.pos.all_currency,function(currency1){
                    if(currency1.id == parseInt(attrs.currentTarget.value.split("-")[2])){
                        self.pos.currency['id'] = currency1.id;
                        self.pos.currency['symbol']= currency1.symbol;
                        self.pos.currency['position']= currency1.position;
                        default_currency = false;
                    }
                });
                if(default_currency){
                    self.pos.currency['id'] = self.pos.currency_temp_id;
                    self.pos.currency['symbol']= self.pos.currency_temp_symbol;
                    self.pos.currency['position']= self.pos.currency_temp_position;
                }
                self.pos.get('selectedOrder').attributes.pricelist_id = self.pos.current_pricelist;
            });

            $("#options").click(function(){
               flag = 0;
                _.each(self.pos.attributes.orders.models, function(order){
                    if( order.attributes.reserved_seat)
                        flag ++;
                });
                if(flag){
                    $(".table_dialog").show();
                    $(".table_content").remove();
                    $(".order_dialog").remove();
                    $(".order_screen").remove();
                    self.pos_widget.screen_selector.set_current_screen('table_screen');
                }
            });

            $("#back_screen").click(function(){
                var previous = self.pos.get('selectedOrder').get_screen_data('previous-screen');
                self.pos_widget.screen_selector.set_current_screen(previous);
            });

            $( ".oe_sidebar_print" ).bind( "click", function() {
                self.pos.option_value = '';
                self.pos.option_text = $(this).text();
                self.pos.option_value = $(this).attr("id");
                if(self.pos.option_value  == "synchronize_order"){
                    self.synchronize_order(true);
                }else{
                    self.booked_table = [];
                    flag = 0;
                    _.each(self.pos.attributes.orders.models, function(order){
                        if(order.attributes.reserved_seat)
                            flag ++;
                    });
                    if(flag){
                        self.pos.openDialog(false, true);
                    }
                }
            });

            if(!self.pos.config.display_send_to_kitchen){
                $("#send_to_kitchen").css("display","none");
            }

            if(! self.pos.config.display_print_receipt){
                $("#print_receipt_button").css("display","none");
            }

            _.each(self.pos.user_list, function(user){
                if(user.id == self.pos.get('selectedOrder').attributes.driver_name){
                    $("#user_selection option:contains(" + user.name + ")").attr('selected', 'selected');
                }
            });

            if(! self.pos.get('selectedOrder').attributes.driver_name){
                $("#user_selection option:contains(" + self.pos.user.name + ")").attr('selected', 'selected');
            }else if(self.pos.get('selectedOrder').attributes.driver_name){
                $("#optionPartner").val(self.pos.get('selectedOrder').attributes.creationDate);
            }

            $("#user_selection option:contains(" + self.pos.user.name + ")").attr('selected', 'selected');
            $('#user_selection option[value=""]').remove();
            $("#user_selection").change(function(ev){
                self.change_user(parseInt($(this).val()));
            });

            $('#print_receipt_button').click(function(){
                if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                    alert(_t("Can not Print order which have no order line"));
                    return false;
                }else{
                    var currentOrder = self.pos.get('selectedOrder');
                    $(".order_screen").remove();
                    currentOrder.attributes.pricelist_id = parseInt($("#pricelist_selection" ).val());
                    self.pos_order_dataset.call("create_from_ui", [[currentOrder.export_as_JSON()], true,false]).then(function(order_id){
                        self.pos.attributes.selectedOrder.attributes.id = order_id[0];
                        self.synchronize_order(false);
                        setTimeout(function(){
                            for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].ol_flag = false;
                                self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                    if(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.pos.attributes.selectedOrder.attributes.reserved_seat){
                                        self.pos.attributes.selectedOrder.attributes.orderLines.remove(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                    }
                                }
                            }
                        },300);
                    });
                    //$('#print_receipt_button').attr("disabled","disabled");
                    self.pos.kitchen_receipt = true;
                    self.pos.customer_receipt = true;
                    var currentOrder = self.pos.get('selectedOrder');
                    currentOrder.kitchen_receipt = true;
                    currentOrder.customer_receipt = false;
                    _.each(currentOrder.get('orderLines').models, function(order_line){
                        order_line.categ_name = "All";
                        order_line.product_name = order_line.product.display_name;
                        order_line.print_qty = order_line.quantity;
                        order_line.print = true;
                        order_line.ol_flag = false;
                    });
                    self.receipt_screen.refresh();
                    if(self.pos.config.iface_print_via_proxy){
                        var receipt = currentOrder.export_for_printing();
                        self.pos.proxy.print_receipt(QWeb.render('kitchen_receipt',{
                            receipt: receipt, widget: self,order:currentOrder,orderlines: currentOrder.get('orderLines').models,
                        }));
                    }else{
                        self.pos_widget.screen_selector.set_current_screen('receipt');
                        self.add_categ_button();
                    }
                }
            });

            $("#order_confirm_button").click(function(e){
                self.pos.kitchen_receipt = false;
                self.pos.customer_receipt = true;
                if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                      alert(_t("Can not confirm order which have no order line"));
                      return false;
                }else{
                    $(".order_screen").remove();
                    var currentOrder = self.pos.get('selectedOrder');
                    currentOrder.attributes.pricelist_id = parseInt($("#pricelist_selection" ).val());
                    currentOrder.kitchen_receipt = false;
                    currentOrder.customer_receipt = true;
                    self.receipt_screen.refresh();
                    self.pos_widget.screen_selector.set_current_screen('receipt');
                    self.pos_order_dataset.call("create_from_ui", [[currentOrder.export_as_JSON()], false,true]).then(function(order_id){
                        self.pos.attributes.selectedOrder.attributes.id = order_id[0];
                        self.synchronize_order(false);
                        setTimeout(function(){
                            for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                for( idx in self.pos.attributes.selectedOrder.attributes.orderLines.models){
                                    self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].line_id = order_id[1][idx];
                                    if(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx].id == undefined && self.pos.attributes.selectedOrder.attributes.reserved_seat){
                                        self.pos.attributes.selectedOrder.attributes.orderLines.remove(self.pos.attributes.selectedOrder.attributes.orderLines.models[idx]);
                                    }
                                }
                            }
                        },300);
                    });
                }
            });

            $('#print_customer_receipt').click(function(){
               if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                   alert(_t("Can not Print order which have no order line"));
                   return false;
               }else{
                   $(".order_screen").remove();
                   self.pos.kitchen_receipt = false;
                   self.pos.customer_receipt = true;
                   self.print_all_products = [];
                   var currentOrder = self.pos.get('selectedOrder');
                   currentOrder.kitchen_receipt = false;
                   currentOrder.customer_receipt = true;
                   self.receipt_screen.print_receipt();
                   if(self.pos.config.iface_print_via_proxy){
                       var receipt = currentOrder.export_for_printing();
                       self.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                           receipt: receipt, widget: self,order:currentOrder,orderlines: currentOrder.get('orderLines').models,
                       }));
                   }else{
                       self.pos_widget.screen_selector.set_current_screen('receipt');
                       _.each(self.pos.attributes.selectedOrder.attributes.orderLines.models, function(o_l){
                           o_l.print_qty = o_l.quantity;
                       });
                   }
               }
           });
           this.do_call_recursive();
        },

        do_call_recursive: function(){
            var self = this;
            var order_ids = [];
            _.each(this.pos.attributes.orders.models, function(order){
                if(order.attributes.id){
                    order_ids.push(order.attributes.id);
                    clearInterval(self[order.attributes.name.replace(" ", "_")]);
                    $("#"+order.attributes.name.replace(" ", "_")).closest("span").css({"visibility": "visible"});
                }
            });
            if(order_ids != []){
                self.synchronize_order(false);
                self.pos_order_dataset.call("get_done_orderline", [order_ids]).then(function(callback){
                    _.each(self.pos.attributes.orders.models, function(order){
                        if(callback){
                            _.each(callback, function(ord){
                                _.each(order.attributes.orderLines.models, function(o_line){
                                    if(ord.line_ids.indexOf(o_line.id) >= 0){
                                        o_line.button_red = true;
                                    }else{
                                        o_line.button_red = false;
                                    }
                                });
                                if(ord.id == order.attributes.id){
                                    var set = false;
                                    self[order.attributes.name.replace(" ", "_")] = setInterval(function() {
                                        $("#"+order.attributes.name.replace(" ", "_")).closest("span").css({
                                            "visibility": set ? "hidden" : "visible"
                                        });
                                        set = !set;
                                    }, 800); 
                                }
                            });
                        }else{
                            _.each(order.attributes.orderLines.models, function(o_line){
                                o_line.button_red = false;
                            });
                        }
                    });
                });
                setTimeout(function() { self.do_call_recursive() },10000)
            }else{
                setTimeout(function() { self.do_call_recursive() },10000)
            }
        },
    });

    module.Product = Backbone.Model.extend({
        get_image_url: function(){
            return instance.session.url('/web/binary/image', {model: 'product.product', field: 'image', id: this.get('id')});
        },
    });

    module.OrderWidget.include({
        init : function(parent, options){
            var self = this;
            this._super(parent, options);
            this.editable = false;
            this.pos.bind('change:selectedOrder', this.change_selected_order, this);
            this.line_click_handler = function(event){
                if(!self.editable){
                    return;
                }
                self.pos.get('selectedOrder').selectLine(this.orderline);
                self.product_property(self.pos.get('selectedOrder').selected_orderline.product);
                self.pos_widget.numpad.state.reset();
            };
            this.client_change_handler = function(event){
                self.update_summary();
            };
            this.bind_order_events();
        },

        set_value: function(val) {
            var self = this
            var order = self.pos.get('selectedOrder');
            self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order.line', {}, [] );
            if (self.editable && order.getSelectedLine()) {
                var mode = self.numpad_state.get('mode');
                if( mode === 'quantity'){
                    order.getSelectedLine().set_quantity(val);
                    self.pos_order_dataset.write(order.getSelectedLine().id,{'qty':  order.getSelectedLine().quantity});
                }else if( mode === 'discount'){
                    order.getSelectedLine().set_discount(val);
                    self.pos_order_dataset.write(order.getSelectedLine().id,{'discount':  order.getSelectedLine().discount});
                }else if( mode === 'price'){
                    order.getSelectedLine().set_unit_price(val);
                    self.pos_order_dataset.write(order.getSelectedLine().id,{'price_unit':  order.getSelectedLine().price});
                }
        	}
        },

        product_property : function(product){
            var self = this;
                results = self.pos.all_product;
                if (product.property_ids && product.property_ids.length) {
                    var final_property = [];
                    var sub_property = [];
                    _.each(self.pos.property, function(prop){
                        var find_prop = _.filter(product.property_ids, function(num){ return num == prop.id; });
                        if (find_prop && find_prop.length) {
                            var attributes = [];
                            _.each(results, function(attr){
                                var find_attr = _.filter(prop.product_attribute_ids, function(num){ return num == attr.id; });
                                if (find_attr && find_attr.length){
                                    var checked = false;
                                    _.each(self.pos.get('selectedOrder').selected_orderline.description_ids, function(description_id){
                                        if(description_id == String(prop.id) + "_" + String(attr.id)){
                                            checked = true;
                                        }
                                    });
                                    attributes.push({'name': attr.display_name, 'id': String(prop.id) + "_" + String(attr.id), 'price': attr.list_price, 'image': attr.image_small, 'checked': checked});
                                }
                            });
                            var tmp_obj = {};
                            tmp_obj[prop.name] = {'single': prop.single_choice, 'attirbute': attributes};
                            if (sub_property && sub_property.length >= 1) {
                                sub_property.push(tmp_obj);
                                final_property.push(sub_property);
                                sub_property = [];
                            }
                            else{
                                sub_property.push(tmp_obj);
                            }
                        }
                    });
                    if (sub_property && sub_property.length) {
                        final_property.push(sub_property);
                    }
                    self.final_property = final_property;
                    self.free_text_bool = true;
                    self.open_property_dialog(product);
                }else if(product.is_product_wait || product.is_product_description){
                    self.free_text_bool = false;
                    self.open_property_dialog(product);
                }else if(! product.is_product_wait && ! product.is_product_description){
                    return false;
                }
        },

        open_property_dialog: function(product){
            var self = this;
            self.property_dialog = $(QWeb.render('select-properties', {'widget': self,'product':product})).dialog({
                resizable: false,
                height:"auto",
                width:600,
                title: _t("Select Properties"),
                position: "center",
                modal : 'true',
                close: function( event, ui ) {
                    $( this ).remove();
                },
                buttons: {
                    "Ok": function() {
                        descrip = "";
                        price = 0;
                        description_ids = [];
                        $(this).find('tr td input[type="checkbox"]:checked').each(function(index){
                            value = this.value.split("_");
                            descrip += value[1] +',';
                            price += parseFloat(value[0]);
                            description_ids.push(this.id);
                            this.checked = false;
                        });
                        $(this).find('tr td input[type="radio"]:checked').each(function(){
                            value = this.value.split("_");
                            descrip += value[1] +',';
                            price += parseFloat(value[0]);
                            description_ids.push(this.id);
                            this.checked = false;
                        });
                        if(descrip){
                            descrip = descrip.slice(0,-1);
                        }
                        self.pos.get('selectedOrder').selected_orderline.discription_price = 0;
                        var total_price = self.pos.get('selectedOrder').selected_orderline.price - self.pos.get('selectedOrder').selected_orderline.discription_price;
                        self.pos.get('selectedOrder').selected_orderline.set_unit_price(price + total_price);
                        self.pos.get('selectedOrder').selected_orderline.property_desc = descrip;
                        self.pos.get('selectedOrder').selected_orderline.property_description = descrip;
                        self.pos.get('selectedOrder').selected_orderline.discription_price = price;
                        self.pos.get('selectedOrder').selected_orderline.description_ids = description_ids;
                        self.pos_widget.receipt_screen.refresh();
                        desc = $( "#desc_selection option:selected" ).text();
                        if(desc){
                            if(self.pos.attributes.selectedOrder.selected_orderline.property_description == ''){
                                self.pos.attributes.selectedOrder.selected_orderline.free_text = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.property_desc = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.property_description = desc;
                            }
                            else{
                                self.pos.attributes.selectedOrder.selected_orderline.free_text = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.property_desc = self.pos.attributes.selectedOrder.selected_orderline.property_description + "," +desc;
                                self.pos.attributes.selectedOrder.selected_orderline.property_description = self.pos.attributes.selectedOrder.selected_orderline.property_description + "," +desc;
                            }
                            self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order.line', {}, [] );
                            self.pos_order_dataset.write(self.pos.attributes.selectedOrder.selected_orderline.id,{'property_description':  self.pos.attributes.selectedOrder.selected_orderline.property_description});
                        }
                        if($(".ui-dialog-buttonpane").find(".wait_with").is(":checked")){
                            if(self.pos.attributes.selectedOrder.selected_orderline != 'undefined'){
                                if(product.display_name === self.pos.attributes.selectedOrder.selected_orderline.product.display_name){
                                    self.pos.attributes.selectedOrder.selected_orderline.wait = true;
                                }
                            }
                        }else if(! $(".ui-dialog-buttonpane").find(".wait_with").is(":checked")){
                            self.pos.attributes.selectedOrder.selected_orderline.wait = false;
                        }
                        self.bind_order_events();
                        self.renderElement(); 
                        $( this ).remove();
                    },
                    "Close": function() {
                        $( this ).remove();
                    }
                },
            });

            if(product.is_product_wait){
                $(".ui-dialog-buttonpane").append('<input class="wait_with" type="checkbox" ><b>Wait For Kitchen</b></input>');
            }
            if(! self.free_text_bool){
                $(".ui-dialog-title").text(_t("Description"));
                $(".ui-dialog").css("width","300px");
            }
            if(self.pos.attributes.selectedOrder.selected_orderline.property_description != '' && self.pos.attributes.selectedOrder.selected_orderline.property_description != undefined){
                temp = self.pos.attributes.selectedOrder.selected_orderline.property_description.split(',');
                for (i = 0; i < temp.length; i++) {
                    $("#desc_selection option:contains(" + temp[i] + ")").attr('selected', 'selected');
                }
            }
            if(self.pos.attributes.selectedOrder.selected_orderline.wait){
                $(".ui-dialog-buttonpane").find(".wait_with").attr("checked",true);
            }
        },
    });

    module.OrderButtonWidget.include({
        selectOrder: function(event) {
            var self = this;
            $(".order_dialog").remove();
            $("#options").show();
            $(".oe_dropdown_toggle").css("display","block");
            if(this.order.attributes.pricelist_id){
                self = this;
                for(pricelist in self.pos.pricelists){
                    if(self.pos.pricelists[pricelist].id == self.order.attributes.pricelist_id){
                        $("#pricelist_selection").val(self.order.pos.pricelists[pricelist].id + '-' + self.order.pos.pricelists[pricelist].name + '-'+self.order.pos.pricelists[pricelist].currency_id[0] );
                        self.pos.current_pricelist = self.order.pos.pricelists[pricelist].id;
                        var default_currency = true;
                        _.each(this.order.pos.all_currency,function(currency){
                            if(currency.id == self.order.pos.pricelists[pricelist].currency_id[0]){
                                self.order.pos.currency['id'] = currency.id;
                                self.order.pos.currency['symbol'] = currency.symbol;
                                self.order.pos.currency['position'] = currency.position;
                                default_currency = false;
                            }
                        });
                        if(default_currency){
                            self.pos.currency['id'] = self.pos.currency_temp_id;
                            self.pos.currency['symbol']= self.pos.currency_temp_symbol;
                            self.pos.currency['position']= self.pos.currency_temp_position;
                        }
                    }
                }
            }else{
                var self = this;
                this.order.pos.currency['id'] = this.order.pos.currency_temp_id;
                this.order.pos.currency['symbol']=this.order.pos.currency_temp_symbol;
                this.order.pos.currency['position']=this.order.pos.currency_temp_position;

                _.each(this.pos.pricelists,function(pricelist){
                    if(pricelist.id == self.pos.pricelist.id){
                        $("#pricelist_selection").val(pricelist.id + '-' + pricelist.name  + '-'+ pricelist.currency_id[0] );
                        self.pos.current_pricelist = pricelist.id;
                        self.order.attributes.pricelist_id = parseInt(pricelist.id);
                    }
                });
            }

            $('#print_receipt_button').removeAttr("disabled");
            this.pos.kitchen_receipt = this.order.kitchen_receipt;
            this.pos.customer_receipt = this.order.customer_receipt;
            this.pos.set({
                selectedOrder: this.order
            });
        }
    });

    
    module.Orderline = module.Orderline.extend({
        initialize: function(attr,options){
            this.pos = options.pos;
            this.order = options.order;
            this.product = options.product;
            this.price   = options.product.price;
            this.quantity = 1;
            this.quantityStr = '1';
            this.discount = 0;
            this.discountStr = '0';
            this.type = 'unit';
            this.line_id = null; 
            this.selected = false;
            this.property_desc = options.descrip;
            this.description_ids = options.description_ids;
            this.print = false;
            this.product_pricelist_dataset = new instance.web.DataSetSearch(self, 'product.pricelist', {}, []);
        },

        // return the base price of this product (for this orderline)
        can_be_merged_with: function(orderline){
            if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
                return false;
            }else if(!this.get_unit()){
                return false;
            }else if(this.get_product_type() !== orderline.get_product_type()){
                return false;
            }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
                return false;
            }else if(this.price !== orderline.price){
                return false;
            }else{ 
                return true;
            }
        },

        export_as_JSON: function() {
            return {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: this.get_product().id,
                product_ids: this.get_property_ids(),
                property_description: this.get_property_desc(),
                id: this.get_id(),
                line_id : this.get_line_id(),
                wait_text:this.get_text(),
                button_red: this.button_red ? this.button_red : false
            };
        },

        get_categ_name: function(){
            return this.categ_name;
        },

        get_print_orderline: function(){
            if(this.print){
                return this.print;
            }else return false;
        },

        get_text: function(){
            if(this.wait){
                return this.wait;
            }else return false;
        },

        get_property_ids: function(){
            property_ids = [];
            _.each(this.description_ids, function(line) {
                if (line && line.split('_').length >= 2) {
                    property_ids.push(line.split('_')[1]);
                }
            });
            return [[6, 0, property_ids]];
        },

        get_id: function(){
            return this.id ? this.id : '';
        },

        get_line_id: function(){
            return this.line_id ? this.line_id : '';
        },

        get_property_desc: function(){
            return this.property_description;
        },

        set_property_desc: function(property_desc){
            this.property_desc = property_desc;
            this.property_description = property_desc;
            this.trigger('change',this);
        },

        set_unit_price: function(price){
            this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
            this.trigger('change',this);
        },

        set_discount: function(discount){
            var disc = Math.min(Math.max(parseFloat(discount) || 0, 0),100);
            this.discount = disc;
            this.discountStr = '' + disc;
            this.trigger('change',this);
        },

        set_quantity: function(quantity){
            if(quantity === 'remove'){
                this.order.removeOrderline(this);
                return;
            }else{
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();
                if(unit){
                    if (unit.rounding) {
                        this.quantity    = round_pr(quant, unit.rounding);
                        this.quantityStr = this.quantity.toFixed(Math.ceil(Math.log(1.0 / unit.rounding) / Math.log(10)));
                    } else {
                        this.quantity    = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                }else{
                    this.quantity    = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }
            this.trigger('change',this);
        },
    });

    module.ProductListWidget = module.PosBaseWidget.extend({
        template:'ProductListWidget',
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.model = options.model;
            this.productwidgets = [];
            this.weight = options.weight || 0;
            this.show_scale = options.show_scale || false;
            this.next_screen = options.next_screen || false;

            this.click_product_handler = function(event){
                var product = self.pos.db.get_product_by_id(this.dataset['productId']);
                var quantity = 1;
                if(self.pos.get('selectedOrder').get("orderLines").length){
                    _.each(self.pos.get('selectedOrder').get("orderLines").models, function(orderline) {
                        if(product.display_name == orderline.product.display_name){
                            quantity = orderline.quantity + 1;
                        }
                    });
                }
                if(self.pos.current_pricelist){
                    var product_ids = []
                    results = self.pos.all_product;
                    self.product_pricelist_dataset = new instance.web.DataSetSearch(self, 'product.pricelist', {}, []);
                    self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, []);
                    _.each(self.pos.property, function(prop){
                          var find_prop = _.filter(product.property_ids, function(num){ return num == prop.id; });
                          if (find_prop && find_prop.length) {
                              var attributes = [];
                              _.each(results, function(attr){
                                  var find_attr = _.filter(prop.product_attribute_ids, function(num){ return num == attr.id; });
                                  if (find_attr && find_attr.length) {
                                      product_ids.push(attr.id);
                                  }
                              })
                          }
                      })
                      self.product_pricelist_dataset.call("price_get" , [[self.pos.current_pricelist],product.id, quantity]).done(function(callback){
                        if (callback[parseInt(self.pos.current_pricelist)] != false ){
                            product.list_price = callback[parseInt(self.pos.current_pricelist)];
                            if(self.pos.get('selectedOrder').get("orderLines").models == ''){
                                if(callback[parseInt(self.pos.current_pricelist)] < 0){
                                    product.price = callback[parseInt(self.pos.current_pricelist)] * -1;
                                }
                                else{
                                    product.price = callback[parseInt(self.pos.current_pricelist)];
                                }
                            }else{
                                if(callback[parseInt(self.pos.current_pricelist)] < 0){
                                    product.price = callback[parseInt(self.pos.current_pricelist)] * -1;
                                    product.price += self.discription_price ?  self.discription_price : 0;
                                }
                                else{
                                    product.price = callback[parseInt(self.pos.current_pricelist)];
                                    product.price += self.discription_price ?  self.discription_price : 0;
                                }
                            }
                        }
                        self.pos_order_dataset.call("get_product_price" , [[self.pos.current_pricelist],product_ids, quantity]).done(function(callback){
                            self.pos.product_price_details = callback;
                            options.click_product_action(product);
                        });
                    });
                }

            };

            this.product_list = options.product_list || [];
            this.product_cache = new module.DomCache();
        },

        set_product_list: function(product_list){
            this.product_list = product_list;
            this.renderElement();
        },

        get_product_image_url: function(product){
            return window.location.origin + '/web/binary/image?model=product.product&field=image_medium&id='+product.id;
        },

        replace: function($target){
            this.renderElement();
            var target = $target[0];
            target.parentNode.replaceChild(this.el,target);
        },

        render_product: function(product){
            var cached = this.product_cache.get_node(product.id);
            if(!cached){
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{ 
                        widget:  this, 
                        product: product, 
                        image_url: this.get_product_image_url(product),
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id,product_node);
                return product_node;
            }
            return cached;
        },

        renderElement: function() {
            var self = this;

            // this._super()
            var el_str  = openerp.qweb.render(this.template, {widget: this});
            var el_node = document.createElement('div');
                el_node.innerHTML = el_str;
                el_node = el_node.childNodes[1];

            if(this.el && this.el.parentNode){
                this.el.parentNode.replaceChild(el_node,this.el);
            }
            this.el = el_node;

            var list_container = el_node.querySelector('.product-list');
            for(var i = 0, len = this.product_list.length; i < len; i++){
                var product_node = this.render_product(this.product_list[i]);
                product_node.addEventListener('click',this.click_product_handler);
                list_container.appendChild(product_node);
            };
        },
    });

    module.ProductScreenWidget.include({
        start: function(){
            var self = this;
            this.product_list_widget = new module.ProductListWidget(this,{
                click_product_action: function(product){
                    results = self.pos.all_product;
                    if (product.property_ids && product.property_ids.length) {
                        var final_property = [];
                        var sub_property = [];
                        _.each(self.pos.property, function(prop){
                            var find_prop = _.filter(product.property_ids, function(num){ return num == prop.id; });
                            if (find_prop && find_prop.length) {
                                var attributes = [];
                                _.each(results, function(attr){
                                    var find_attr = _.filter(prop.product_attribute_ids, function(num){ return num == attr.id; });
                                    if (find_attr && find_attr.length) {
                                        if(self.pos.current_pricelist){
                                            _.each(self.pos.product_price_details,function(record){
                                                if(record.id == attr.id){
                                                    var checked = false;
                                                    if(self.pos.get('selectedOrder').selected_orderline){
                                                        _.each(self.pos.get('selectedOrder').selected_orderline.description_ids, function(description_id){
                                                            if(description_id == String(prop.id) + "_" + String(attr.id)){
                                                                checked = true;
                                                            }
                                                        });
                                                        attributes.push({'name': attr.display_name, 'id': String(prop.id) + "_" + String(attr.id), 'price': Math.round(record.data[self.pos.current_pricelist]*100) / 100, 'image': attr.image_small, 'checked': checked});
                                                    }else{
                                                        attributes.push({'name': attr.display_name, 'id': String(prop.id) + "_" + String(attr.id), 'price': Math.round(record.data[self.pos.current_pricelist]*100) / 100, 'image': attr.image_small, 'checked': false});
                                                    }
                                                }
                                            })
                                        }else{
                                            var checked = false;
                                            if(self.pos.get('selectedOrder').selected_orderline){
                                                _.each(self.pos.get('selectedOrder').selected_orderline.description_ids, function(description_id){
                                                    if(description_id == String(prop.id) + "_" + String(attr.id)){
                                                        checked = true;
                                                    }
                                                });
                                                attributes.push({'name': attr.display_name, 'id': String(prop.id) + "_" + String(attr.id), 'price': attr.price, 'image': attr.image_small, 'checked': checked});
                                            }else{
                                                attributes.push({'name': attr.display_name, 'id': String(prop.id) + "_" + String(attr.id), 'price': attr.price, 'image': attr.image_small, 'checked': false});
                                            }
                                        }
                                    }
                                });
                                var tmp_obj = {};
                                tmp_obj[prop.name] = {'single': prop.single_choice, 'attirbute': attributes};
                                if (sub_property && sub_property.length >= 1) {
                                    sub_property.push(tmp_obj);
                                    final_property.push(sub_property);
                                    sub_property = [];
                                }
                                else{
                                    sub_property.push(tmp_obj);
                                }
                            }
                        });
                        if (sub_property && sub_property.length) {
                            final_property.push(sub_property);
                        }
                        self.final_property = final_property;
                        self.free_text_bool = true;
                        self.open_prop_dialog(product);
                    }else{
                        if(product.is_product_description || product.is_product_wait){
                            self.free_text_bool = false;
                            self.open_prop_dialog(product);
                        }
                        if(! product.is_product_description && ! product.is_product_wait){ 
                            if(product.to_weight && self.pos.iface_electronic_scale){
                                self.pos_widget.screen_selector.set_current_screen(self.scale_screen, {product: product});
                            }else{
                                self.pos.get('selectedOrder').addProduct(product);
                            }
                        }
                    }
                },
                product_list: this.pos.db.get_product_by_category(0)
            });
            this.product_list_widget.replace(this.$('.placeholder-ProductListWidget'));
            this.product_categories_widget = new module.ProductCategoriesWidget(this,{
                product_list_widget: this.product_list_widget,
            });
            this.product_categories_widget.replace(this.$('.placeholder-ProductCategoriesWidget'));
        },

        open_prop_dialog: function(product){
            var self = this;
            self.property_dialog = $(QWeb.render('select-properties', {'widget': self,'product':product})).dialog({
                resizable: false,
                title: _t("Select Properties"),
                width:600,
                modal : 'true',
                close: function( event, ui ) {
                    $( this ).remove();
                },
                buttons: {
                    "Ok": function() {
                        descrip = "";
                        price = 0;
                        description_ids = [];
                        $(this).find('tr td input[type="checkbox"]:checked').each(function(index){
                            if(this.id){
                                value = this.value.split("_");
                                descrip += value[1] +',';
                                price += parseFloat(value[0]);
                                description_ids.push(this.id);
                                this.checked = false;
                            }else{
                                product.price = parseFloat(this.value);
                            }
                        });
                        $(this).find('tr td input[type="radio"]:checked').each(function(){
                            value = this.value.split("_");
                            descrip += value[1] +',';
                            price += parseFloat(value[0]);
                            description_ids.push(this.id);
                            this.checked = false;
                        });
                        desc = $( "#desc_selection option:selected" ).text();
                        if(descrip){
                            if(desc){
                                descrip = descrip.slice(0,-1) + ","+desc;
                            }else{
                                descrip = descrip.slice(0,-1);
                            }
                        }
                        if(product.to_weight && self.pos.iface_electronic_scale){
                            self.pos_widget.screen_selector.set_current_screen(self.scale_screen, {product: product});
                        }else{
                            self.pos.get('selectedOrder').addProduct(product, descrip, price, description_ids);
                        }
                        if(desc){
                            if(descrip){
                                self.pos.attributes.selectedOrder.selected_orderline.free_text = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.set_property_desc(descrip);
                                self.pos.attributes.selectedOrder.selected_orderline.property_desc = descrip;
                                self.pos.attributes.selectedOrder.selected_orderline.property_description = descrip;
                            }
                            if(! descrip){
                                self.pos.attributes.selectedOrder.selected_orderline.free_text = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.set_property_desc(desc);
                                self.pos.attributes.selectedOrder.selected_orderline.property_desc = desc;
                                self.pos.attributes.selectedOrder.selected_orderline.property_description = desc;
                            }
                            self.pos_order_dataset = new instance.web.DataSetSearch(this, 'pos.order.line', {}, [] );
                            self.pos_order_dataset.write(self.pos.attributes.selectedOrder.selected_orderline.id,{'property_description':  self.pos.attributes.selectedOrder.selected_orderline.property_description});
                        }
                        if($(".ui-dialog-buttonpane").find(".wait_with").is(":checked")){
                            if(self.pos.attributes.selectedOrder.selected_orderline != 'undefined'){
                                if(product.display_name === self.pos.attributes.selectedOrder.selected_orderline.product.display_name){
                                    self.pos.attributes.selectedOrder.selected_orderline.wait = true;
                                }
                            }else if(! $(".ui-dialog-buttonpane").find(".wait_with").is(":checked")){
                                self.pos.attributes.selectedOrder.selected_orderline.wait = false;
                            }
                        }
                        $( this ).remove();
                    },
                    "Close": function() {
                        $(".pos").show();
                        $( this ).remove();
                    }
                },
            });

            if(product.is_product_wait){
                $(".ui-dialog-buttonpane").append('<input class="wait_with" type="checkbox" ><b>Wait For Kitchen</b></input>');
            }
            if(! self.free_text_bool){
                $(".ui-dialog-title").text(_t("Description"));
                $(".ui-dialog").css("width","300px");
            }
            if(self.pos.attributes.selectedOrder.selected_orderline){
                if(product.display_name == self.pos.attributes.selectedOrder.selected_orderline.product.display_name){
                    if(self.pos.attributes.selectedOrder.selected_orderline.property_description !== ''){
                        temp = self.pos.attributes.selectedOrder.selected_orderline.property_description.split(',');
                        for (i = 0; i < temp.length; i++) {
                            $("#desc_selection option:contains(" + temp[i] + ")").attr('selected', 'selected');
                        }
                        $("#wait_text").val(self.pos.attributes.selectedOrder.selected_orderline.free_text);
                    }
                    if(self.pos.attributes.selectedOrder.selected_orderline.wait){
                        $(".ui-dialog-buttonpane").find(".wait_with").attr("checked",true);
                    }
                }
            }
        },
    });

    module.ReceiptScreenWidget = module.ScreenWidget.extend({
        template: 'ReceiptScreenWidget',

        show_numpad:     true,
        show_leftpane:   true,

        print_receipt: function(){
            this.currentOrder = this.pos.get('selectedOrder');
            this.currentOrderLines = (this.pos.get('selectedOrder')).get('orderLines');
            this.print_all_products = [];
            var self = this;
            _.each(this.currentOrderLines.models, function(order_line){
                order_line.categ_name = "All";
                self.print_all_products.push(order_line);
                order_line.product_name = order_line.product.display_name;
                order_line.print_qty = order_line.quantity;
                order_line.print = true;
            });
        },

        show: function(){
            this._super();
            var self = this;
            var is_kitchen = self.pos.kitchen_receipt;
            if(is_kitchen){
                self.pos_widget.add_categ_button();
            }

            if(!is_kitchen){
                var print_button = this.add_action_button({
                        label: _t('Print'),
                        icon: '/point_of_sale/static/src/img/icons/png48/printer.png',
                        click: function(){ self.print(); },
                    });

                if(! self.pos.customer_receipt){
                    var finish_button = this.add_action_button({
                            label: _t('Next Order'),
                            icon: '/point_of_sale/static/src/img/icons/png48/go-next.png',
                            click: function() { self.finishOrder(); },
                        });
                    finish_button.set_disabled(true);
                    setTimeout(function(){
                        finish_button.set_disabled(false);
                    }, 2000);
                }
            }
            if(self.pos && (is_kitchen) || self.pos.customer_receipt){
                this.add_action_button({
                        label: _t('Back'),
                        icon: '/point_of_sale/static/src/img/icons/png48/go-previous.png',
                        click: function() {
                            $('#print_receipt_button').removeAttr("disabled");
                            self.pos_widget.screen_selector.set_current_screen('products');
                        },
                   });
            }

            this.refresh();
            this.print();

          //
          // The problem is that in chrome the print() is asynchronous and doesn't
          // execute until all rpc are finished. So it conflicts with the rpc used
          // to send the orders to the backend, and the user is able to go to the next 
          // screen before the printing dialog is opened. The problem is that what's 
          // printed is whatever is in the page when the dialog is opened and not when it's called,
          // and so you end up printing the product list instead of the receipt... 
          //
          // Fixing this would need a re-architecturing
          // of the code to postpone sending of orders after printing.
          //
          // But since the print dialog also blocks the other asynchronous calls, the
          // button enabling in the setTimeout() is blocked until the printing dialog is 
          // closed. But the timeout has to be big enough or else it doesn't work
          // 2 seconds is the same as the default timeout for sending orders and so the dialog
          // should have appeared before the timeout... so yeah that's not ultra reliable. 

//          finish_button.set_disabled(true);
//          setTimeout(function(){
//              finish_button.set_disabled(false);
//          }, 2000);
        },

        print: function() {
            window.print();
        },

        finishOrder: function() {
            this.pos.get('selectedOrder').destroy();
        },

        refresh: function() {
            var order = this.pos.get('selectedOrder');
            $('.pos-receipt-container', this.$el).html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                }));
        },

        close: function(){
            this._super();
        },
    });

    module.PaymentScreenWidget.include({
        validate_order: function(options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            if(!this.is_paid()){
                return;
            }

            if(    this.pos.config.iface_cashdrawer 
                && this.pos.get('selectedOrder').get('paymentLines').find( function(pl){ 
                           return pl.cashregister.journal.type === 'cash'; 
                   })){
                    this.pos.proxy.open_cashbox();
            }

            product_list = [];
            price_list = [];
            _.each(currentOrder.attributes.orderLines.models, function(order_line){
                product_list.push(order_line.product.display_name);
                price_list.push(self.pos_widget.format_currency(order_line.get_display_price()));
            });
            self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
            self.pos_order_dataset.call("pole_display", [product_list,price_list,validate = true,currentOrder.getDiscountTotal().toFixed(2)]);
            if(options.invoice){
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation',true);
                this.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);


                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').destroy();
                });

            }else{
                this.pos.push_order(currentOrder);
                if(this.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    this.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,order:self.pos.get('selectedOrder')
                    }));
                    this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }else{
                    this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                }
            }

            // hide onscreen (iOS) keyboard 
            setTimeout(function(){
                document.activeElement.blur();
                $("input").blur();
            },250);
        },
    });

    module.NumpadWidget.include({
        start: function() {
            this.state.bind('change:mode', this.changedMode, this);
            this.changedMode();
            this.pin_code_dataset = new instance.web.DataSetSearch(self, 'pin.code', {}, [] );
            this.$el.find('.numpad-backspace').click(_.bind(this.clickDeleteLastChar, this));
            this.$el.find('.numpad-minus').click(_.bind(this.clickSwitchSign, this));
            this.$el.find('.number-char').click(_.bind(this.clickAppendNewChar, this));
            this.$el.find('.mode-button').click(_.bind(this.clickChangeMode, this));
            if(this.pos.config.pincode){
                this.$el.find('.mode-button').click(_.bind(this.open_pincode_dialog, this));
            }
        },

        clickDeleteLastChar: function() {
            self = this;
            if(this.pos.get('selectedOrder').selected_orderline.id && (this.state.get('mode') != 'price') &&( this.state.get('mode') != 'discount')){
                (new instance.web.Model('pos.order.line')).get_func('orderline_state_id')(this.pos.get('selectedOrder').selected_orderline.id).then(function(state_id){
                    if(state_id == 1){
                        self.pos_orderline_dataset = new instance.web.DataSetSearch(self, 'pos.order.line', {}, []);
                        self.pos_orderline_dataset.unlink([self.pos.get('selectedOrder').selected_orderline.id]);
                        self.state.deleteLastChar();
                        return self.state.deleteLastChar();
                    }
                    else if(state_id != 1){
                        alert("Current orderline is not remove");
                        return false;
                    }
                });
            }
            if(! this.pos.get('selectedOrder').selected_orderline.id ){
                return this.state.deleteLastChar();
            }else if(this.pos.get('selectedOrder').selected_orderline.id && (this.state.get('mode') == 'price' || this.state.get('mode') == 'discount')){
                return this.state.deleteLastChar();
            }
        },

        open_pincode_dialog: function() {
            var self = this;
            if(self.pos.attributes.selectedOrder.attributes.orderLines.models == ''){
                alert(_t('Please Select Product !!'));
                return false;
            }else if(self.state.get('mode') !== "quantity" && self.pos.config.pincode){
                $(QWeb.render('Pincode', {'widget': self})).dialog({
                    resizable: false,
                    height:160,
                    modal: true,
                    close: function( event, ui ) {
                        self.state.changeMode("quantity");
                        $( this ).remove();
                     },
                    title: _t("Pin Code"),
                    buttons: {
                        "Ok": function() {
                            var dialog = this;
                            code = $("#inputcode").val();
                            if(code){
                                self.pin_code_dataset.call("pin_code",[code]).then(function(callback){
                                    if(! callback){
                                        alert(_t("Please Enter Correct Pin code"));
                                        $("#inputcode").val('');
                                        $("#inputcode").focus();
                                    }else{
                                        $(dialog).remove();
                                    }
                                });
                            }else{
                                alert(_t("Please Enter Pin code"));
                            }
                        },
                    },
                });
            }
        },
    });

    instance.web_kanban.KanbanGroup.include({
       compute_cards_auto_height: function() {
           // oe_kanban_no_auto_height is an empty class used to disable this feature
           if (!this.view.group_by) {
               var min_height = 0;
               var els = [];
               _.each(this.records, function(r) {
                   var $e = r.$el.children(':first:not(.oe_kanban_no_auto_height)').css('min-height', 0);
                   if ($e.length) {
                       els.push($e[0]);
                       min_height = Math.max(min_height, $e.outerHeight());
                   }
               });
          // $(els).css('min-height', min_height);
           }
       },
   });

    module.SplitbillScreenWidget = module.ScreenWidget.extend({
        template: 'SplitbillScreenWidget',

        show_leftpane:   false,
        previous_screen: 'products',

        renderElement: function(){
            var self = this;
            this._super();
            var order = this.pos.get('selectedOrder');
            if(!order){
                return;
            }
            var orderlines = order.get('orderLines').models;
            for(var i = 0; i < orderlines.length; i++){
                var line = orderlines[i];
                linewidget = $(QWeb.render('SplitOrderline',{ 
                    widget:this, 
                    line:line, 
                    selected: false,
                    quantity: 0,
                    id: line.id,
                }));
                linewidget.data('id',line.id);
                this.$('.orderlines').append(linewidget);
            }
            this.$('.back').click(function(){
                self.pos_widget.screen_selector.set_current_screen(self.previous_screen);
            });
        },

        lineselect: function($el,order,neworder,splitlines,line_id){
            var split = splitlines[line_id] || {'quantity': 0, line: null};
            split.id = line_id;
            var line  = order.getOrderline(line_id);

            if( ! line.get_unit().groupable ){
                if( split.quantity !== line.get_quantity()){
                    split.quantity = line.get_quantity();
                }else{
                    split.quantity = 0;
                }
            }else{
                if( split.quantity < line.get_quantity()){
                    split.quantity += line.get_unit().rounding;
                    if(split.quantity > line.get_quantity()){
                        split.quantity = line.get_quantity();
                    }
                }else{
                    split.quantity = 0;
                }
            }

            if( split.quantity ){
                if ( !split.line ){
                    split.line = line.clone();
                    neworder.addOrderline(split.line);
                }
                split.line.set_quantity(split.quantity);
            }else if( split.line ) {
                neworder.removeOrderline(split.line);
                split.line = null;
            }

            splitlines[line_id] = split;
            $el.replaceWith($(QWeb.render('SplitOrderline',{
                widget: this,
                line: line,
                selected: split.quantity !== 0,
                quantity: split.quantity,
                id: line_id,
            })));
            this.$('.order-info .subtotal').text(this.format_currency(neworder.getSubtotal()));
        },

        pay: function($el,order,neworder,splitlines,cashregister_id){
            var orderlines = order.get('orderLines').models;
            var empty = true;
            var full  = true;

            for(var i = 0; i < orderlines.length; i++){
                var id = orderlines[i].id;
                var split = splitlines[id];
                if(!split){
                    full = false;
                }else{
                    if(split.quantity){
                        empty = false;
                        if(split.quantity !== orderlines[i].get_quantity()){
                            full = false;
                        }
                    }
                }
            }

            if(empty){
                return;
            }

            for(var i = 0; i < this.pos.cashregisters.length; i++){
                if(this.pos.cashregisters[i].id === cashregister_id){
                    var cashregister = this.pos.cashregisters[i];
                    break;
                }
            }

            if(full){
                order.addPaymentline(cashregister);
                this.pos_widget.screen_selector.set_current_screen('payment');
            }else{
                _.each(splitlines,function(s_line) {
                   var line  = order.getOrderline(parseInt(s_line.id));
                    if(s_line.id == line.id){
                        self.pos_line = new instance.web.DataSetSearch(self, 'pos.order.line');
                        self.pos_order = new instance.web.DataSetSearch(self, 'pos.order');
                        self.pos_order.call('search_read', [[['id', '=', order.attributes.id]]]).then(function(record){
                            _.each(record[0].lines,function(line_id) {  
                                if(line_id == line.id){
                                    self.pos_line.unlink(line.id);
                                }
                            });
                        });
                    }
                });
                for(var id in splitlines){
                    var split = splitlines[id];
                    var line  = order.getOrderline(parseInt(id));
                    line.set_quantity(line.get_quantity() - split.quantity);
                    if(Math.abs(line.get_quantity()) < 0.00001){
                        order.removeOrderline(line);
                    }
                    delete splitlines[id];
                }
                neworder.addPaymentline(cashregister);
                neworder.set_screen_data('screen','payment');

                // for the kitchen printer we assume that everything
                // has already been sent to the kitchen before splitting 
                // the bill. So we save all changes both for the old 
                // order and for the new one. This is not entirely correct 
                // but avoids flooding the kitchen with unnecessary orders. 
                // Not sure what to do in this case.

                if ( neworder.saveChanges ) { 
                    order.saveChanges();
                    neworder.saveChanges();
                }

                this.pos.get('orders').add(neworder);
                this.pos.set('selectedOrder',neworder);
            }
        },

        show: function(){
            var self = this;
            this._super();
            this.renderElement();

            var order = this.pos.get('selectedOrder');
            var neworder = new module.Order({
                pos: this.pos,
                temporary: true,
            });
            neworder.set('client',order.get('client'));
            neworder.set('pflag',order.get('pflag'));
            neworder.set('parcel',order.get('parcel'));
            neworder.set('pricelist_id',order.get('pricelist_id'));
            neworder.set('phone',order.get('phone'));
            neworder.set('partner_id',order.get('partner_id'));
            neworder.set('driver_name',order.get('driver_name'));
            neworder.set('creationDate',order.get('creationDate'));
            neworder.set('table_data',order.get('table_data'));
            neworder.set('split',true);

            var splitlines = {};

            this.$('.orderlines').on('click','.orderline',function(){
                var id = parseInt($(this).data('id'));
                var $el = $(this);
                self.lineselect($el,order,neworder,splitlines,id);
            });

            this.$('.paymentmethod').click(function(){
                var id = parseInt($(this).data('id'));
                var $el = $(this);
                self.pay($el,order,neworder,splitlines,id);
            });
        },
    });

    module.OrderScreenWidget = module.ScreenWidget.extend({
        template : "OrderScreenWidget",
    });

    module.TableScreenWidget = module.ScreenWidget.extend({
        template : "TableScreenWidget",
    });

    module.ScreenSelector.include({
        set_current_screen: function(screen_name,params,refresh){
            var screen = this.screen_set[screen_name];
            var self = this
            if(screen_name == 'dialog'){
                $(".pos-leftpane").hide();
                $(".order_screen_content").show();
            }else{
                $(".pos-leftpane").show();
                $(".order_screen_content").hide();
            }
            if(!screen){
                console.error("ERROR: set_current_screen("+screen_name+") : screen not found");
            }

            this.close_popup();

            var order = this.pos.get('selectedOrder');
            var old_screen_name = order.get_screen_data('screen');

            order.set_screen_data('screen',screen_name);

            if(params){
                order.set_screen_data('params',params);
            }

            if( screen_name !== old_screen_name ){
                order.set_screen_data('previous-screen',old_screen_name);
            }

            if ( refresh || screen !== this.current_screen){
                if(this.current_screen){
                    this.current_screen.close();
                    this.current_screen.hide();
                }
                this.current_screen = screen;
                this.current_screen.show();
            }
        },
    });

    module.ClientListScreenWidget.include({
         // what happens when we've just pushed modifications for a partner of id partner_id
        saved_client_details: function(partner_id){
            var self = this;
            this.reload_partners().then(function(){
                var partner = self.pos.db.get_partner_by_id(partner_id);
                self.pos.partners.push(partner);
                if (partner) {
                    self.new_client = partner;
                    self.toggle_save_button();
                    self.display_client_details('show',partner);
                } else {
                    // should never happen, because create_from_ui must return the id of the partner it
                    // has created, and reload_partner() must have loaded the newly created partner. 
                    self.display_client_details('hide');
                }
            });
        },

        save_changes: function(){
            var self = this
            if( this.has_client_changed() ){
                this.pos.get('selectedOrder').set_client(this.new_client);
                if(this.pos.get('selectedOrder').attributes.id){
                    self.pos_order_dataset = new instance.web.DataSetSearch(self, 'pos.order', {}, [] );
                    self.pos_order_dataset.write(this.pos.get('selectedOrder').attributes.id,{'partner_id':  this.new_client.id})
                }
            }
        },
    });
};
