# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import base64
import tempfile
from openerp.tools.translate import _
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from time import gmtime, strftime
from openerp import tools
import time


class e_tax_wiz(osv.osv):
    _inherit = "account.common.account.report"
    _name = 'e.tax.wiz'


    _columns = {
            'year_id': fields.many2one('account.fiscalyear', 'Year'),
    }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        context.update({'year_id': data['fiscalyear_id'], 'datas': data})
        return {
          'name': _('Binary'),
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'binary.e.tax.text.file.wizard',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
        }

class binary_e_tax_text_file_wizard(osv.osv_memory):
    _name = 'binary.e.tax.text.file.wizard'

    sold_accounts = {}

    def _sum_debit_account(self, cr, uid, account, context=None):
        obj_move = self.pool.get('account.move.line')
        context.update({'fiscalyear': context.get('datas').get('fiscalyear_id')[0]})
        query = obj_move._query_get(cr, uid, obj='l', context=context)
        if account.type == 'view':
            return account.debit
        move_state = ['draft', 'posted']
        if context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', '']
        cr.execute('SELECT sum(debit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND ' + query + ' '
                , (account.id, tuple(move_state)))
        sum_debit = cr.fetchone()[0] or 0.0
#        if context.get('datas').get('init_balance'):
#            cr.execute('SELECT sum(debit) \
#                    FROM account_move_line l \
#                    JOIN account_move am ON (am.id = l.move_id) \
#                    WHERE (l.account_id = %s) \
#                    AND (am.state IN %s) \
#                    AND '+ init_query +' '
#                    ,(account.id, tuple(move_state)))
#            # Add initial balance to the result
#            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit

    def _sum_credit_account(self, cr, uid, account, context=None):
        obj_move = self.pool.get('account.move.line')
        context.update({'fiscalyear': context.get('datas').get('fiscalyear_id')[0]})
        query = obj_move._query_get(cr, uid, obj='l', context=context)
        if account.type == 'view':
            return account.credit
        move_state = ['draft', 'posted']
        if context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', '']
        cr.execute('SELECT sum(credit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND ' + query + ' '
                , (account.id, tuple(move_state)))
        sum_credit = cr.fetchone()[0] or 0.0
#        if self.init_balance:
#            self.cr.execute('SELECT sum(credit) \
#                    FROM account_move_line l \
#                    JOIN account_move am ON (am.id = l.move_id) \
#                    WHERE (l.account_id = %s) \
#                    AND (am.state IN %s) \
#                    AND '+ self.init_query +' '
#                    ,(account.id, tuple(move_state)))
#            # Add initial balance to the result
#            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit

    def _sum_balance_account(self, cr, uid, account, context=None):
        if account.type == 'view':
            return account.balance
        obj_move = self.pool.get('account.move.line')
        move_state = ['draft', 'posted']
#         context.update({'fiscalyear': context.get('datas').get('fiscalyear_id')[0]})
        query = obj_move._query_get(cr, uid, obj='l', context=context)
        if context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', '']
        cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND ' + query + ' '
                , (account.id, tuple(move_state)))
        sum_balance = cr.fetchone()[0] or 0.0
#        if self.init_balance:
#            cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
#                    FROM account_move_line l \
#                    JOIN account_move am ON (am.id = l.move_id) \
#                    WHERE (l.account_id = %s) \
#                    AND (am.state IN %s) \
#                    AND '+ self.init_query +' '
#                    ,(account.id, tuple(move_state)))
#            # Add initial balance to the result
#            sum_balance += cr.fetchone()[0] or 0.0
        return sum_balance

    def get_children_accounts(self, cr, uid, account, context=None):
        res = []
        obj_move = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        ids_acc = self.pool.get('account.account')._get_children_and_consol(cr, uid, account.id)
        currency = account.currency_id and account.currency_id or account.company_id.currency_id
        fiscal_year_id = context.get('datas').get('fiscalyear_id')[0]
#         context.update({'fiscalyear': fiscal_year_id})
        query = obj_move._query_get(cr, uid, obj='l', context=context)
        for child_account in self.pool.get('account.account').browse(cr, uid, ids_acc, context=context):
            sql = """
                SELECT count(id)
                FROM account_move_line AS l
                WHERE %s AND l.account_id = %%s
            """ % (query)
            cr.execute(sql, (child_account.id,))
            num_entry = cr.fetchone()[0] or 0
            sold_account = self._sum_balance_account(cr, uid, child_account, context=context)
            self.sold_accounts[child_account.id] = sold_account
            if context.get('datas').get('display_account') == 'movement':
                if child_account.type != 'view' and num_entry <> 0:
                    res.append(child_account)
            elif context.get('datas').get('display_account') == 'not_zero':
                if child_account.type != 'view' and num_entry <> 0:
                    if not currency_obj.is_zero(cr, uid, currency, sold_account):
                        res.append(child_account)
            else:
                res.append(child_account)
        if not res:
            return [account]
        return res

    def lines(self, cr, uid, account, context=None):
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft', 'posted']
        obj_move = self.pool.get('account.move.line')
#         context.update({'fiscalyear': context.get('datas').get('fiscalyear_id')[0]})
        query = obj_move._query_get(cr, uid, obj='l', context=context)
        init_query = obj_move._query_get(cr, uid, obj='l', context=context)
        if context.get('datas').get('target_move') == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        sql = """
            SELECT m1.move_id,
                array_to_string(ARRAY(SELECT DISTINCT a.code
                                          FROM account_move_line m2
                                          LEFT JOIN account_account a ON (m2.account_id=a.id)
                                          WHERE m2.move_id = m1.move_id
                                          AND m2.account_id<>%%s), ', ') AS counterpart
                FROM (SELECT move_id
                        FROM account_move_line l
                        LEFT JOIN account_move am ON (am.id = l.move_id)
                        WHERE am.state IN %s and %s AND l.account_id = %%s GROUP BY move_id) m1
        """ % (tuple(move_state), query)
        cr.execute(sql, (account.id, account.id))
        counterpart_res = cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

#        if self.sortby == 'sort_journal_partner':
#        sql_sort='j.code, p.name, l.move_id'
#        else:
        sql_sort = 'l.date, l.move_id'
        sql = """
            SELECT l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, l.partner_id AS lpartner_id,
            m.name AS move_name, m.id AS mmove_id,per.code as period_code,
            c.symbol AS currency_code,
            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number,
            p.name AS partner_name
            FROM account_move_line l
            JOIN account_move m on (l.move_id=m.id)
            LEFT JOIN res_currency c on (l.currency_id=c.id)
            LEFT JOIN res_partner p on (l.partner_id=p.id)
            LEFT JOIN account_invoice i on (m.id =i.move_id)
            LEFT JOIN account_period per on (per.id=l.period_id)
            JOIN account_journal j on (l.journal_id=j.id)
            WHERE %s AND m.state IN %s AND l.account_id = %%s ORDER by %s
        """ % (query, tuple(move_state), sql_sort)
        cr.execute(sql, (account.id,))
        res_lines = cr.dictfetchall()
        res_init = []
        if res_lines and context.get('datas').get('init_balance'):
            # FIXME: replace the label of lname with a string translatable
            sql = """
                SELECT 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, '' AS lperiod_id, '' AS lpartner_id,
                '' AS move_name, '' AS mmove_id, '' AS period_code,
                '' AS currency_code,
                NULL AS currency_id,
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,
                '' AS partner_name
                FROM account_move_line l
                LEFT JOIN account_move m on (l.move_id=m.id)
                LEFT JOIN res_currency c on (l.currency_id=c.id)
                LEFT JOIN res_partner p on (l.partner_id=p.id)
                LEFT JOIN account_invoice i on (m.id =i.move_id)
                JOIN account_journal j on (l.journal_id=j.id)
                WHERE %s AND m.state IN %s AND l.account_id = %%s
            """ % (init_query, tuple(move_state))
            cr.execute(sql, (account.id,))
            res_init = cr.dictfetchall()
        res = res_init + res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*' + str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']].replace(', ', ',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
#            if l['amount_currency'] != None:
#                tot_currency = tot_currency + l['amount_currency']
        return res

    def _generate_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        res_users_obj = self.pool.get('res.users')
        period_id = []
        if context and context.get('year_id'):
            period_id.append(context.get('year_id')[0])
        start_date = end_date = False
        if period_id:
            period_data = self.pool.get('account.fiscalyear').browse(cr, uid, period_id[0])
            start_date = period_data.date_start
            end_date = period_data.date_stop
        company_data = res_users_obj.browse(cr, uid, uid).company_id
        purchase_order_obj = self.pool.get('purchase.order')
        acc_invoice_obj = self.pool.get('account.invoice')
        tax_obj = self.pool.get('account.tax')
        tax_code_obj = self.pool.get('account.tax.code')
        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        cur_obj = self.pool.get('res.currency')
        
        cust_arg = [('type', '=', 'out_invoice'), ('state', 'in', ['open', 'paid'])]
        supp_arg = [('type', '=', 'in_invoice'), ('state', 'in', ['open', 'paid'])]

        if start_date:
            cust_arg.append(('date_invoice', '>=', start_date))
            supp_arg.append(('date_invoice', '>=', start_date))
            
        if end_date:
            cust_arg.append(('date_invoice', '<=', end_date))
            supp_arg.append(('date_invoice', '<=', end_date))
                    
        customer_invoice_ids = acc_invoice_obj.search(cr, uid, cust_arg)
        supplier_invoice_ids = acc_invoice_obj.search(cr, uid, supp_arg)
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            company_record = tools.ustr('CompInfoStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('CompanyName|CompanyUEN|GSTNo|PeriodStart|PeriodEnd|IAFCreationDate|ProductVersion|IAFVersion||||||') + \
                            "\r\n" + \
                            tools.ustr(company_data and company_data.name or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.company_uen or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.gst_no or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.period_start and datetime.datetime.strptime(company_data.period_start, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.period_end and datetime.datetime.strptime(company_data.period_end, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.iaf_creation_date and datetime.datetime.strptime(company_data.iaf_creation_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.product_version or '') + \
                            '|'.ljust(1) + \
                            tools.ustr(company_data and company_data.iaf_version or '') + \
                            '|'.ljust(1) + \
                            "\r\n" + \
                            tools.ustr('CompInfoEnd|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('PurcDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('SupplierName|SupplierUEN|InvoiceDate|InvoiceNo|PermitNo|LineNo|ProductDescription|PurchaseValueSGD|GSTValueSGD|TaxCode|FCYCode|PurchaseFCY|GSTFCY') + \
                            "\r\n"
            tmp_file.write(company_record)
            tot_line = 0
            tot_pur_sgd = tot_gst_sg = 0.0
            for supplier in acc_invoice_obj.browse(cr, uid, supplier_invoice_ids):
                line_no = 1
                for line in supplier.invoice_line:
                    SupplierName = supplier.partner_id.name or ''
                    SupplierUEN = supplier.partner_id.supplier_uen or ''
                    InvoiceDate = supplier and supplier.date_invoice and datetime.datetime.strptime(supplier.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or ''
                    InvoiceNo = supplier.supplier_invoice_number or ''
                    PermitNo = supplier.permit_no or ''
                    LineNo = line_no
                    ProductDescription = line.name or ''
                    
                    if supplier.currency_id.id == supplier.company_id.currency_id.id:
                        PurchaseValueSGD = line.price_subtotal or 0.0
                        GSTValueSGD = 0.0
                        TaxCode = ''
                        FCYCode = 'XXX'
                        PurchaseFCY = 0.0
                        GSTFCY = 0.0
                        
                    else:
                        PurchaseValueSGD = cur_obj.compute(cr, uid, supplier.currency_id.id, supplier.company_id.currency_id.id, line.price_subtotal, context={'date': supplier.date_invoice})
                        GSTValueSGD = 0.0
                        TaxCode = ''
                        FCYCode = supplier.currency_id.name or ''
                        PurchaseFCY = line.price_subtotal or 0.0
                        GSTFCY = 0.0
                    tot_pur_sgd += PurchaseValueSGD
                    
                    for tax in line.invoice_line_tax_id:
                        tax_amt = tax_amt_foreign = 0.0
                        tax_name = ''
                        tax_data = tax_obj.compute_all(cr, uid, [tax], (line.price_unit * (1 - (line.discount or 0.0) / 100.0)), line.quantity, line.product_id, supplier.partner_id)['taxes']
                        if tax_data:
                            tax_amt = tax_data[0]['amount']
                            tax_name = tax_code_obj.browse(cr, uid, tax_data[0].get('tax_code_id')).code
                        if supplier.currency_id.id == supplier.company_id.currency_id.id:
                            GSTValueSGD = tax_amt
                            TaxCode = tax_name or ''
                            GSTFCY = 0.0
                        else:
                            GSTValueSGD = cur_obj.compute(cr, uid, supplier.currency_id.id, supplier.company_id.currency_id.id, tax_amt, context={'date': supplier.date_invoice})
                            TaxCode = tax_name or ''
                            GSTFCY = tax_amt
                        tot_gst_sg += GSTValueSGD
                        
                    supplier_record = tools.ustr(SupplierName) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(SupplierUEN) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(InvoiceDate) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(InvoiceNo) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(PermitNo) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(int(LineNo)) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(ProductDescription) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(PurchaseValueSGD) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(GSTValueSGD) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(TaxCode) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(FCYCode) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(PurchaseFCY) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(GSTFCY) + \
                                      '|'.ljust(1) + \
                                      "\r\n"
                    tmp_file.write(supplier_record)
                    line_no += 1
                    tot_line += 1
            customer_data = tools.ustr('PurcDataEnd|') + \
                            tools.ustr(float(tot_pur_sgd) or 0.0) + \
                            '|'.ljust(1) + \
                            tools.ustr(float(tot_gst_sg) or 0.0) + \
                            '|'.ljust(1) + \
                            tools.ustr(int(tot_line)) + \
                            '||||||||||'.ljust(1) + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('SuppDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('CustomerName|CustomerUEN|InvoiceDate|InvoiceNo|LineNo|ProductDescription|SupplyValueSGD|GSTValueSGD|TaxCode|Country|FCYCode|SupplyFCY|GSTFCY|') + \
                            "\r\n"
            tmp_file.write(customer_data)
            
            tot_supp_line_no = 0
            tot_supp_sgd = tot_gst_sg = 0.0
            for customer in acc_invoice_obj.browse(cr, uid, customer_invoice_ids):
                supp_line_no = 1
                for line in customer.invoice_line:

                    CustomerName = customer.partner_id.name or ''
                    CustomerUEN = customer.partner_id.customer_uen or ''
                    InvoiceDate = customer and customer.date_invoice and datetime.datetime.strptime(customer.date_invoice, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or ''
                    InvoiceNo = customer.number or ''
                    LineNo = supp_line_no
                    ProductDescription = line.name or ''
                    Country = customer.partner_id.country_id and customer.partner_id.country_id.name or ''
                    
                    if customer.currency_id.id == customer.company_id.currency_id.id:
                        SupplyValueSGD = line.price_subtotal or 0.0
                        GSTValueSGD = 0.0
                        TaxCode = ''
                        FCYCode = 'XXX'
                        SupplyFCY = 0.0
                        GSTFCY = 0.0
                    else:
                        SupplyValueSGD = cur_obj.compute(cr, uid, customer.currency_id.id, customer.company_id.currency_id.id, line.price_subtotal, context={'date': customer.date_invoice})
                        GSTValueSGD = 0.0
                        TaxCode = ''
                        FCYCode = customer.currency_id.name or ''
                        SupplyFCY = line.price_subtotal or 0.0
                        GSTFCY = 0.0
                    tot_supp_sgd += SupplyValueSGD
                    
                    for tax in line.invoice_line_tax_id:
                        tax_amt = tax_amt_foreign = 0.0
                        tax_name = ''
                        tax_data = tax_obj.compute_all(cr, uid, [tax], (line.price_unit * (1 - (line.discount or 0.0) / 100.0)), line.quantity, line.product_id, customer.partner_id)['taxes']
                        if tax_data:
                            tax_amt = tax_data[0]['amount']
                            tax_name = tax_code_obj.browse(cr, uid, tax_data[0].get('tax_code_id')).code
                        if customer.currency_id.id == customer.company_id.currency_id.id:
                            GSTValueSGD = tax_amt
                            TaxCode = tax_name or ''
                            GSTFCY = 0.0
                        else:
                            GSTValueSGD = cur_obj.compute(cr, uid, customer.currency_id.id, customer.company_id.currency_id.id, tax_amt, context={'date': customer.date_invoice})
                            TaxCode = tax_name or ''
                            GSTFCY = tax_amt
                        tot_gst_sg += GSTValueSGD

                 
                    supplier_record = tools.ustr(CustomerName) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(CustomerUEN) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(InvoiceDate) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(InvoiceNo) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(int(LineNo)) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(ProductDescription).encode('ascii', 'ignore').decode('ascii')+ \
                                      '|'.ljust(1) + \
                                      tools.ustr(SupplyValueSGD) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(GSTValueSGD) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(TaxCode) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(Country) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(FCYCode) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(float(SupplyFCY)) + \
                                      '|'.ljust(1) + \
                                      tools.ustr(GSTFCY) + \
                                      '|'.ljust(1) + \
                                      "\r\n"
                    tmp_file.write(supplier_record)
                    supp_line_no += 1
                    tot_supp_line_no += 1
            account_data = tools.ustr('SuppDataEnd|') + \
                            tools.ustr(float(tot_supp_sgd) or 0.0) + \
                            '|'.ljust(1) + \
                            tools.ustr(float(tot_gst_sg) or 0.0) + \
                            '|'.ljust(1) + \
                            tools.ustr(int(tot_supp_line_no)) + \
                            '||||||||||'.ljust(1) + \
                            "\r\n" + \
                            tools.ustr('|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('GLDataStart|||||||||||||') + \
                            "\r\n" + \
                            tools.ustr('TransactionDate|AccountID|AccountName|TransactionDescription|Name|TransactionID|SourceDocumentID|SourceType|Debit|Credit|Balance|||') + \
                            "\r\n"
            tmp_file.write(account_data)
            
            
            account = account_obj.browse(cr, uid, context.get('datas').get('chart_account_id')[0])
            child_data = self.get_children_accounts(cr, uid, account, context=context)
            for acc in child_data:
                obj_period = self.pool.get('account.period')
                ctx = {'fiscalyear':context.get('datas').get('fiscalyear_id')[0]}
                period_ids = obj_period.search(cr, uid, [('fiscalyear_id', '=', context.get('datas').get('fiscalyear_id')[0]), ('special', '=', True)])
                ctx.update({'datas': context.get('datas'), 'periods':period_ids})
                
                debit_amt = self._sum_debit_account(cr, uid, acc, context=ctx)
                credit_amt = self._sum_credit_account(cr, uid, acc, context=ctx)
                balance_account = self._sum_balance_account(cr, uid, acc, context=ctx)
                opening_balance = tools.ustr(datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                  '|'.ljust(1) + \
                                  tools.ustr(acc.code) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(acc.name) + \
                                  '|'.ljust(1) + \
                                  tools.ustr('OPENING BALANCE') + \
                                  '|||||'.ljust(1) + \
                                  tools.ustr(debit_amt or 0.0) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(credit_amt or 0.0) + \
                                  '|'.ljust(1) + \
                                  tools.ustr(balance_account or 0.0) + \
                                  '|||'.ljust(1) + \
                                  "\r\n"
                tmp_file.write(opening_balance)
                acc_data = self.lines(cr, uid, acc, context=context)
                for ac in acc_data:
                    move_data = tools.ustr(datetime.datetime.strptime(ac.get('ldate'), DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(acc.code) + \
                                '|'.ljust(1) + \
                                tools.ustr(acc.name) + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('lname') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('partner_name') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('mmove_id') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('lref') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('line_corresp') or '') + \
                                '|'.ljust(1) + \
                                tools.ustr(float(ac.get('debit')) or 0.0) + \
                                '|'.ljust(1) + \
                                tools.ustr(float(ac.get('credit')) or 0.0) + \
                                '|'.ljust(1) + \
                                tools.ustr(ac.get('progress') or 0.0) + \
                                '|'.ljust(1) + \
                                "\r\n"
                    tmp_file.write(move_data)
                    
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        return base64.b64encode(out)


    _columns = {
        'name': fields.char('Name', size=64),
        'etax_txt_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }

    _defaults = {
         'name': 'ETAX.txt',
         'etax_txt_file': _generate_file,
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
