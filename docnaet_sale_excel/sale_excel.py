#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class SaleOrder(orm.Model):
    """ Model name: SaleOrder
    """
    
    _inherit = 'sale.order'
    
    def extract_sale_excel_report(self, cr, uid, context=None):
        ''' Schedule extract of sale quotation info
        '''
        # Pool used:
        excel_pool = self.pool.get('excel.writer')
        docnaet_document = self.pool.get('docnaet.document')
        sale_pool = self.pool.get('sale.order')
        
        # Collect data:
        partner_total = {}
        product_total = {}
        month_column = []

        # ---------------------------------------------------------------------
        # Docnaet Order:
        # ---------------------------------------------------------------------               
        ws_name = 'Offerte'
        excel_pool.create_worksheet(name=ws_name)
        width = [
            40, 20, 12, 12, 45,
            3, 15,
            15,
            ]
        header = [
            'Partner', 'Commerciale', 'Data', 'Scadenza', 'Oggetto', 
            'Val.', 'Totale', 
            'Scoperto cliente',
            ]
            
        sale_ids = sale_pool.search(cr, uid, [
            ('state', 'in', ('draft','sent','cancel')),
            ], context=context)

        row = 0
                
        # Format:
        excel_pool.set_format()
        f_title = excel_pool.get_format('title')
        f_header = excel_pool.get_format('header')
        f_text = excel_pool.get_format('text')
        f_text_red = excel_pool.get_format('text_red')
        f_number = excel_pool.get_format('number')
        f_number_red = excel_pool.get_format('number_red')
        
        # Column:
        excel_pool.column_width(ws_name, width)
        
        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)
        row += 1   
        
        sale_proxy = sale_pool.browse(
            cr, uid, sale_ids, context=context)
        for order in sorted(
                sale_proxy, 
                key=lambda x: x.date_order,
                reverse=True):
            partner = order.partner_id

            # -----------------------------------------------------------------            
            # Partner total:
            # -----------------------------------------------------------------            
            if partner not in partner_total:
                partner_total[partner] = [
                    0.0, # Order
                    0.0, # Quotation
                    0.0, # Lost
                    ]
            partner_total[partner][0] += order.amount_untaxed # TODO Currency
            
            # -----------------------------------------------------------------            
            # Product total:
            # -----------------------------------------------------------------            
            for line in order.order_line:
                product = line.product_id
                if not product:
                    continue
                deadline = (line.date_deadline or ' No')[:7]
                if product not in product_total:
                    product_total[product] = {}
                if deadline in product_total[product]:
                    product_total[product][deadline] += line.product_uom_qty
                else:    
                    product_total[product][deadline] = line.product_uom_qty
                if deadline not in month_column:
                    month_column.append(deadline)    

            # -----------------------------------------------------------------            
            # Excel write detail:
            # -----------------------------------------------------------------            
            if partner.duelist_uncovered:
                f_text_current = f_text_red
                f_number_current = f_number_red
            else:
                f_text_current = f_text
                f_number_current = f_number
            excel_pool.write_xls_line(
                ws_name, row, [
                    partner.name,
                    order.user_id.name,
                    order.date_order,
                    order.date_deadline,
                    order.name,
                    '',
                    (order.amount_untaxed, f_number_current),                    
                    (partner.duelist_uncovered_amount or '', f_number_current),             
                    ], default_format=f_text_current)
            row += 1
        month_column = sorted(month_column)
        
        # ---------------------------------------------------------------------
        # Docnaet Quotation (pending and lost):
        # ---------------------------------------------------------------------   
        # Setup:
        ws_setup = [
            ('Quotazioni', [
                ('sale_state', '=', 'pending'),
                ('sale_order_amount', '>', 0.0),
                ]),
            ('Perse', [
                ('sale_state', '=', 'lost'),
                ('sale_order_amount', '>', 0.0),
                ]),
            ]

        width = [
            40, 20, 12, 12, 45,
            3, 15,
            15,
            ]
        header = [
            'Partner', 'Commerciale', 'Data', 'Scadenza', 'Oggetto', 
            'Val.', 'Totale', 
            'Scoperto cliente',
            ]
            
        for ws_name, document_filter in ws_setup:
            docnaet_ids = docnaet_document.search(
                cr, uid, document_filter, context=context)
            if not docnaet_ids:    
                continue # Not written

            excel_pool.create_worksheet(name=ws_name)
            row = 0
                    
            # Column:
            excel_pool.column_width(ws_name, width)
            
            # Header:
            excel_pool.write_xls_line(
                ws_name, row, header, default_format=f_header)
            row += 1   

            document_proxy = docnaet_document.browse(
                cr, uid, docnaet_ids, context=context)
            for document in sorted(
                    document_proxy, 
                    key=lambda x: x.date,
                    reverse=True):
                partner = document.partner_id
                if partner not in partner_total:
                    partner_total[partner] = [
                        0.0, # Order
                        0.0, # Quotation
                        0.0, # Lost
                        ]
                if ws_name == 'Quotazioni':        
                    partner_total[partner][1] += order.amount_untaxed #XXX Curre
                else:    
                    partner_total[partner][2] += order.amount_untaxed #XXX Curre

                if partner.duelist_uncovered:
                    f_text_current = f_text_red
                    f_number_current = f_number_red
                else:
                    f_text_current = f_text
                    f_number_current = f_number
                excel_pool.write_xls_line(
                    ws_name, row, [
                        partner.name,
                        document.user_id.name,
                        document.date,
                        document.deadline,
                        '%s %s' % (
                            document.name or '',
                            document.description or '',
                            ),
                        document.sale_currency_id.symbol,
                        (document.sale_order_amount, f_number_current),                    
                        (partner.duelist_uncovered_amount or '', 
                            f_number_current),             
                        ], default_format=f_text_current)
                row += 1

        # ---------------------------------------------------------------------
        # Docnaet Customer total:
        # ---------------------------------------------------------------------               
        ws_name = 'Clienti'
        excel_pool.create_worksheet(name=ws_name)
        width = [40, 20, 20, 20, 30, ]
        header = [
            'Partner', 'Offerte', 'Quotazioni', 'Perse', 
            'Scoperto cliente',
            ]
        row = 0
                
        # Column:
        excel_pool.column_width(ws_name, width)
        
        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)
        row += 1   
        
        for partner in sorted(partner_total, key=lambda x: x.name):
            order, quotation, lost = partner_total[partner]
            excel_pool.write_xls_line(
                ws_name, row, [
                    partner.name,
                    (order or '', f_number),                    
                    (quotation or '', f_number),       
                    (lost or '', f_number_red),                    
                    (partner.duelist_uncovered_amount or '', f_number_red),
                    ], default_format=f_text_current)
            row += 1

        # ---------------------------------------------------------------------
        # Docnaet Product total:
        # ---------------------------------------------------------------------               
        ws_name = 'Prodotti'
        excel_pool.create_worksheet(name=ws_name)
        width = [15, 40, 2, 10]
        width.extend([8 for item in range(0, len(month_column))])
        empty = ['' for item in range(0, len(month_column))]

        header = ['Codice', 'Prodotto', 'UM', 'Totale']
        start = len(header)
        header.extend(month_column)        
                
        # Column:
        row = 0
        excel_pool.column_width(ws_name, width)
        
        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)        
        for product in sorted(product_total, key=lambda x: x.default_code):
            row += 1   
            data = [
                product.default_code, 
                product.name, 
                product.uom_id.account_ref or product.uom_id.name]
            data.extend(empty)
            excel_pool.write_xls_line(
                ws_name, row, data, 
                default_format=f_text)
            total = 0.0
            for deadline in product_total[product]:
                subtotal = int(product_total[product][deadline])
                excel_pool.write_xls_line(
                    ws_name, row, [
                        subtotal, 
                        ],
                        default_format=f_number, 
                        col=start + month_column.index(deadline))
                        
            excel_pool.write_xls_line(
                ws_name, row, [
                    total, 
                    ], 
                    default_format=f_number, 
                    col=start-1)

        # ---------------------------------------------------------------------
        # Send mail:
        # ---------------------------------------------------------------------        
        return excel_pool.send_mail_to_group(cr, uid, 
            'docnaet_sale_excel.group_sale_statistic_mail', 
            'Statistiche vendite', 
            'Statistiche giornaliere vendite', 
            'sale_statistic.xlsx',
            context=context)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
