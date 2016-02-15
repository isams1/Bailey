from openerp.osv import osv, fields

class acc_report(osv.TransientModel):
    
    _name = 'acc.report'
    
    _columns = {
        'group_type':fields.selection([('by_location', 'By Location'), ('by_country', 'By Country')], string="Filter"),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        loc_obj = self.pool.get('res.partner')
        comp_obj = self.pool.get('res.company')
        country_obj = self.pool.get('res.country')
        acc_obj = self.pool.get('accommodation.accommodation')
        bed_obj = self.pool.get('beds.beds')
        visa_obj = self.pool.get('visa.quota')
        loc_ids = loc_obj.search(cr, uid, [('location', '=', True)], context=context)
        cr.execute('select distinct(v.nationality_id),c.name from visa_quota v, res_country c where v.nationality_id=c.id')
        res = cr.fetchall()
        country_ids = [tpl[0] for tpl in res]
        countries = dict([(tpl[0], tpl[1]) for tpl in res])
        company_ids = comp_obj.search(cr, uid, [('tenant', '=', True)], context=context)
        companies = dict([(comp.id, comp.code) for comp in comp_obj.browse(cr, uid, company_ids, context=context)])
        list_new = []
        if wiz_rec.group_type == 'by_location':
            loc_dict = {}
            locs = []
            comp = []
            lst = []
            new_lst = []
            for loc in loc_obj.browse(cr, uid, loc_ids, context=context):
                acc_ids = acc_obj.search(cr, uid, [('address_id', '=', loc.id)], context=context)
                new_dict = {'sr_no' : loc.name + ', ' + str(loc.contact_address).replace("\n", ", "),
                        'acc_name' : '',
                        'country':[],
                        'landlord':'',
                        'tenant':'',
                        'max':'',
                        'occupied':'',
                        'available':'',
                        'location' : 1}
                if acc_ids:
                    new_lst.append(new_dict)
                count = 0
                for accom in acc_obj.browse(cr, uid, acc_ids, context=context):
                    count += 1
                    visa_dict = {}
#                    accom_lst = []
                    for visa in accom.visa_quota_ids:
                        acco_address = accom.address_id.name
                        company_dict = {}
                        country_comp_total = 0
                        for company_id in company_ids:
                            args = [
                                ('room_id.accommodation_id', '=', accom.id),
                                ('employee_id', '!=', False),
                                ('employee_id.company_id', '=', company_id),
                                ('employee_id.emp_country_id', '=', visa.nationality_id.id)
                            ]
                            bed_ids_filled = bed_obj.search(cr, uid, args, context=context, count=True)
                            country_comp_total += bed_ids_filled
                            company_dict[companies.get(company_id)] = bed_ids_filled
                        company_dict['total'] = country_comp_total
                        visa_dict[visa.nationality_id.name] = company_dict
                    country_lst = []
                    for key, val in visa_dict.iteritems():
                        country_dict = {}
                        country_dict['country'] = key
                        country_dict.update(val)
                        country_lst.append(country_dict)
                    new_dict = {
                        'sr_no' : count,
                        'acc_name' : accom.name,
                        'country':country_lst,
                        'landlord':accom.land_lord_id.name,
                        'tenant':accom.paying_comp_id.code,
                        'max':accom.maximum_capacity,
                        'occupied':accom.stay_capacity,
                        'available':accom.occupied,
                        'location' : 0
                        }
                    new_lst.append(new_dict)
#                loc_dict[loc.name] = accom_lst
#                locs.append(loc.name)
#                comp.append(companies)
            ret_dict = {'loc_dict1' : new_lst}
            res = {'ids': ids, 'model':'acc.report', 'form': ret_dict}
            return self.pool['report'].get_action(cr, uid, [], 'accommodation.view_location_report', data=res, context=context)
        elif wiz_rec.group_type == 'by_country':
            country_dict = {}
            for country in country_obj.browse(cr, uid, country_ids, context=context):
                loc_dict = {}
                country_id = country.id
                visa_ids = visa_obj.search(cr, uid, [('nationality_id', '=', country_id)], context=context)
                for visa in visa_obj.browse(cr, uid, visa_ids, context=context):
                    loc_name = visa.accommodation_id.address_id.name
                    acc_dict = {}
                    company_dict = {}
                    visa_total = visa.number_of_quota
                    visa_avail = visa.quota_available
                    visa_occupied = visa_total - visa_avail
                    country_comp_total = 0
                    for company in comp_obj.browse(cr, uid, company_ids, context=context):
                        company_id = company.id
                        args = [
                            ('employee_id.company_id', '=', company_id),
                            ('employee_id', '!=', False),
                            ('employee_id.emp_country_id', '=', visa.nationality_id.id),
                            ('room_id.accommodation_id', '=', visa.accommodation_id.id)
                        ]
                        occupied_beds = bed_obj.search(cr, uid, args, context=context, count=True)
                        country_comp_total += occupied_beds
                        company_dict[company.code] = occupied_beds
                        company_dict.update({'acc_name' : visa.accommodation_id.name})
                    company_dict['total'] = country_comp_total
                    if loc_name in loc_dict.keys():
                        loc_dict[loc_name]['acc_list'].append(company_dict)
                        loc_dict[loc_name]['max'] += visa_total
                        loc_dict[loc_name]['occupied'] += visa_occupied
                        loc_dict[loc_name]['available'] += visa_avail
                    else:
                        loc_dict[loc_name] = {'acc_list':[company_dict], 'max':visa_total, 'occupied':visa_occupied, 'available':visa_avail}
                country_dict[country.name] = loc_dict
            final_dict = {}
            final_list = []
            for con_key, con_val in country_dict.iteritems():
                final_dict = {
                    'sr_no':con_key,
                    'max':'',
                    'loc' : '',
                    'occupied':'',
                    'available':'',
                    'acc_list':[],
                    'country' : 1
                }
                final_list.append(final_dict)
                counter = 0
                for loc_key, loc_val in con_val.iteritems():
                    counter += 1
                    final_dict = {
                    'sr_no':counter,
                    'max':loc_val.get('max', 0),
                    'loc' : loc_key,
                    'occupied':loc_val.get('occupied', 0),
                    'available':loc_val.get('available', 0),
                    'acc_list':loc_val.get('acc_list', []),
                    'country' : 0
                    }
                    final_list.append(final_dict)
            ret_dict = {'loc_dict' : loc_dict, 'loc_dict1' : final_list}
            res = {'ids': ids, 'model':'acc.report', 'form': ret_dict}
            return self.pool['report'].get_action(cr, uid, [], 'accommodation.view_nationality_report', data=res, context=context)
