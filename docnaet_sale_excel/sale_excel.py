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


class ResPartner(orm.Model):
    """ Model name: Res Partner
    """

    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    # Import procedure:
    # -------------------------------------------------------------------------
    def import_account_agent_reference(self, cr, uid, fullname, context=None):
        """ Import Agent reference
        """
        agent_cache = {}

        i = 0
        _logger.info('Start import Agent')
        for line in open(fullname, 'r'):
            i += 1
            line = line.strip()
            if not line:
                _logger.warning('%s. Jump line: empty line' % i)
                continue

            row = line.split('|')
            partner_code = row[0].strip()
            # partner_name = row[1].strip()

            agent_code = row[2].strip()
            agent_name = row[3].strip()

            commercial_code = row[4].strip()
            commercial_name = row[5].strip()

            if not partner_code:
                _logger.warning('%s. Jump line: partner code empty' % i)
                continue

            partner_ids = self.search(cr, uid, [
                '|', '|',
                ('sql_customer_code', '=', partner_code),
                ('sql_supplier_code', '=', partner_code),
                ('sql_destination_code', '=', partner_code),
                ], context=context)

            if not partner_ids:
                _logger.warning('%s. Jump line: partner not found' % i)
                continue

            # -----------------------------------------------------------------
            # SQL agent_id part:
            # -----------------------------------------------------------------
            agent_id = False
            if agent_code in agent_cache:
                agent_id = agent_cache[agent_code]
            else:
                agent_ids = self.search(cr, uid, [
                    ('sql_supplier_code', '=', agent_code),
                ], context=context)
                if agent_ids:
                    agent_id = agent_ids[0]
                    agent_cache[agent_code] = agent_id

            self.write(cr, uid, partner_ids, {
                'account_reference1_code': agent_code,
                'account_reference1_name': agent_name,
                'account_reference2_code': commercial_code,
                'account_reference2_name': commercial_name,

                # SQL mx_agent_id part:
                'agent_id': agent_id,
                }, context=context)
            _logger.info('%s. Update line: %s' % (i, partner_code))
        _logger.info('Start import Agent')
        return True

    _columns = {
        'account_reference1_code': fields.char('Codice Agente', size=9),
        'account_reference1_name': fields.char('Nome Agente', size=40),
        'account_reference2_code': fields.char('Codice Commerciale', size=9),
        'account_reference2_name': fields.char('Nome Commerciale', size=40),
        'account_reference3_code': fields.char('Codice Responsabile', size=9),
        'account_reference3_name': fields.char('Nome Responsabile', size=40),
        }


class SaleOrder(orm.Model):
    """ Model name: SaleOrder
    """

    _inherit = 'sale.order'

    # Function:
    def get_partner_note(self, partner):
        """ Return color information
        """
        return '%s%s' % (
            '[Pagamenti scaduti presenti] ' if
            partner.duelist_uncovered else '',

            '[Fuori FIDO] ' if
            partner.duelist_over_fido else '',
        )

    # -------------------------------------------------------------------------
    # Report procedure:
    # -------------------------------------------------------------------------
    # Salesman:
    def extract_sale_excel_report(self, cr, uid, context=None):
        """ Schedule extract of sale quotation info
        """

        if context is None:
            context = {}

        save_mode = context.get('save_mode')
        _logger.info('Start extract save mode: %s' % save_mode)

        # Pool used:
        excel_pool = self.pool.get('excel.writer')
        docnaet_document = self.pool.get('docnaet.document')
        sale_pool = self.pool.get('sale.order')

        # Collect data:
        partner_total = {}  # Statistic for partner
        product_total = {}  # Statistic for product
        month_column = []
        now = ('%s' % datetime.now())[:7]

        # ---------------------------------------------------------------------
        # Docnaet Order:
        # ---------------------------------------------------------------------
        ws_name = 'Ordini'
        excel_pool.create_worksheet(name=ws_name)
        width = [
            45, 20, 20,
            # 20,
            8, 10, 10,
            20, 3, 13,
            3, 13, 13, 13, 40,
            ]
        header = [
            'Cliente', 'Nazione', 'Responsabile',
            # 'Agente',
            'Tipo', 'Data', 'Scad./Merce pronta',
            'N. ordine Mexal', 'Val.', 'Totale',
            'Val.', 'Pag. aperti', 'Di cui scaduti', 'FIDO', 'Note',
            ]

        sale_ids = sale_pool.search(cr, uid, [
            ('accounting_order', '=', True),  # Confirmed order
            ('logistic_state', '!=', 'done'),  # Not closed
            # todo consider only active lines!!!
            ], context=context)

        _logger.warning('Total order found: %s' % len(sale_ids))
        row = 0

        # Format:
        excel_pool.set_format()
        # f_title = excel_pool.get_format('title')
        f_header = excel_pool.get_format('header')

        f_text = excel_pool.get_format('text')
        f_text_red = excel_pool.get_format('text_red')
        f_text_bg_blue = excel_pool.get_format('bg_blue')

        f_number = excel_pool.get_format('number')
        f_number_red = excel_pool.get_format('number_red')
        f_number_bg_blue = excel_pool.get_format('bg_blue_number')
        f_number_bg_blue_bold = excel_pool.get_format('bg_blue_number_bold')
        f_number_bg_red_bold = excel_pool.get_format('bg_red_number_bold')
        f_number_bg_green_bold = excel_pool.get_format('bg_green_number_bold')

        # Column:
        excel_pool.column_width(ws_name, width)

        sale_proxy = sale_pool.browse(
            cr, uid, sale_ids, context=context)

        total = {}
        temp_list = []
        total_payment_done = []
        for order in sorted(
                sale_proxy,
                key=lambda x: x.date_order,
                reverse=True):
            partner = order.partner_id

            # Currency:
            currency = order.currency_id
            currency_payment = partner.duelist_currency_id or currency

            # -----------------------------------------------------------------
            # COLLECT: Partner total
            # -----------------------------------------------------------------
            if partner not in partner_total:
                partner_total[partner] = {}
            if currency not in partner_total[partner]:
                partner_total[partner][currency] = [
                    0.0,  # Order
                    0.0,  # Quotation
                    0.0,  # Lost
                    ]
            partner_total[partner][currency][0] += order.amount_untaxed

            # -----------------------------------------------------------------
            # Update total:
            # -----------------------------------------------------------------
            if currency not in total:
                # order, exposition, deadlined
                total[currency] = [0.0, 0.0, 0.0]

            if currency_payment not in total:
                # order, exposition, deadlined
                total[currency_payment] = [0.0, 0.0, 0.0]

            total[currency][0] += order.amount_untaxed
            if (partner, currency) not in total_payment_done:  # just once!
                total_payment_done.append((partner, currency))
                total[currency_payment][1] += \
                    partner.duelist_exposition_amount or 0.0
                total[currency_payment][2] += \
                    partner.duelist_uncovered_amount or 0.0

            # -----------------------------------------------------------------
            # Collect data: Product total
            # -----------------------------------------------------------------
            for line in order.order_line:
                if line.logistic_state in ('done', 'cancel'):
                    continue  # Remove line yet delivered (r cancel - need?)

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
            # Setup color:
            if partner.duelist_uncovered or partner.duelist_over_fido:
                f_text_current = f_text_red
                f_number_current = f_number_red
            else:
                f_text_current = f_text
                f_number_current = f_number

            # C E I:
            sql_type = (partner.sql_customer_code or '')[:3]
            if sql_type == '201':
                cei = 'Italia'
            elif sql_type == '230':
                cei = 'CEE'
            elif sql_type == '270':
                cei = 'Extra CEE'
            else:
                cei = ''

            temp_list.append(([
                    '%s [%s]' % (
                        partner.name, partner.sql_customer_code or ''),
                    partner.country_id.name if partner.country_id else
                    'SENZA PAESE',
                    partner.account_reference1_name or '',
                    # partner.account_reference2_name or '',

                    cei,
                    order.date_order,
                    order.date_deadline,

                    order.name,
                    order.currency_id.symbol,  # Order:
                    (order.amount_untaxed, f_number_current),

                    currency_payment.symbol,  # Payment:
                    (partner.duelist_exposition_amount or '',
                        f_number_current),
                    (partner.duelist_uncovered_amount or '',
                        f_number_current),
                    (partner.duelist_fido or '', f_number_current),
                    self.get_partner_note(partner),
                    ], f_text_current))

        month_column = sorted(month_column)
        try:
            index_today = month_column.index(now)
        except:
            index_today = False

        # ---------------------------------------------------------------------
        # Total page order:
        # ---------------------------------------------------------------------
        for currency in sorted(total, key=lambda x: x.symbol):
            excel_pool.write_xls_line(
                ws_name, row, [
                    '', '', '',  # '',
                    '', '', '',
                    'Totale',
                    currency.symbol,  # Order
                    (total[currency][0], f_number_bg_blue_bold),
                    currency.symbol,  # Payment
                    (total[currency][1], f_number_bg_blue_bold),
                    (total[currency][2], f_number_bg_red_bold),
                    ], default_format=f_text_bg_blue)  # , col=6)
            row += 1

        # ---------------------------------------------------------------------
        # Data:
        # ---------------------------------------------------------------------
        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)
        excel_pool.autofilter(ws_name, row, 0, row, len(header) - 1)

        # Record:
        for record, f_text_current in temp_list:
            row += 1
            excel_pool.write_xls_line(
                ws_name, row, record, default_format=f_text_current)

        excel_pool.freeze_panes(ws_name, 3, 1)

        # ---------------------------------------------------------------------
        # Docnaet Quotation (pending and lost):
        # ---------------------------------------------------------------------
        # Setup:
        ws_setup = [
            ('Offerte', [
                ('sale_state', '=', 'pending'),
                ('sale_order_amount', '>', 0.0),
                ]),
            ('Perse', [
                ('sale_state', '=', 'lost'),
                ('sale_order_amount', '>', 0.0),
                ]),
            ]

        width = [
            45, 20, 18, 10, 10, 50,
            3, 12,
            3, 12, 12, 12, 40
            ]
        header = [
            'Cliente', 'Nazione', 'Responsabile', 'Data', 'Scadenza',
            'Oggetto',
            'Val.', 'Totale',
            'Val.', 'Pag. aperti', 'Di cui scaduti', 'FIDO', 'Note',
            ]

        for ws_name, document_filter in ws_setup:
            # todo read Quotation from sale.order not confirmed?
            docnaet_ids = docnaet_document.search(
                cr, uid, document_filter, context=context)
            if not docnaet_ids:
                continue  # Not written

            excel_pool.create_worksheet(name=ws_name)
            row = 0

            # Column:
            excel_pool.column_width(ws_name, width)

            document_proxy = docnaet_document.browse(
                cr, uid, docnaet_ids, context=context)

            excel_pool.freeze_panes(ws_name, 2, 1)

            total = {}
            temp_list = []
            for document in sorted(
                    document_proxy,
                    key=lambda x: x.date,
                    reverse=True):
                partner = document.partner_id
                currency = document.sale_currency_id
                currency_payment = partner.duelist_currency_id or currency

                if partner not in partner_total:
                    partner_total[partner] = {}
                if currency not in partner_total[partner]:
                    partner_total[partner][currency] = [
                        0.0,  # Order
                        0.0,  # Quotation
                        0.0,  # Lost
                        ]
                if ws_name == 'Offerte':
                    partner_total[partner][currency][1] += \
                        document.sale_order_amount
                else:
                    partner_total[partner][currency][2] += \
                        document.sale_order_amount

                # -------------------------------------------------------------
                # Update total in currency mode:
                # -------------------------------------------------------------
                if currency not in total:
                    # order, exposition, deadlined
                    total[currency] = [0.0, 0.0, 0.0]

                if currency_payment not in total:
                    # order, exposition, deadlined
                    total[currency_payment] = [0.0, 0.0, 0.0]

                total[currency][0] += document.sale_order_amount
                total[currency_payment][1] += \
                    partner.duelist_exposition_amount or 0.0
                total[currency_payment][2] += \
                    partner.duelist_uncovered_amount or 0.0

                # Setup color:
                if partner.duelist_uncovered or partner.duelist_over_fido:
                    f_text_current = f_text_red
                    f_number_current = f_number_red
                else:
                    f_text_current = f_text
                    f_number_current = f_number

                temp_list.append(([
                    '%s [%s]' % (
                        partner.name, partner.sql_customer_code or ''),
                    partner.country_id.name if partner.country_id else
                    'SENZA PAESE',
                    document.user_id.name or '',  # Docnaet user
                    document.date,
                    document.deadline,
                    '%s %s' % (
                        document.name or '',
                        document.description or '',
                        ),
                    currency.symbol,
                    (document.sale_order_amount, f_number_current),

                    currency_payment.symbol,
                    (partner.duelist_exposition_amount or '',
                        f_number_current),
                    (partner.duelist_uncovered_amount or '',
                        f_number_current),
                    (partner.duelist_fido or '', f_number_current),
                    self.get_partner_note(partner),
                    ], f_text_current))

            # -----------------------------------------------------------------
            # Total page order:
            # -----------------------------------------------------------------
            for currency in sorted(total, key=lambda x: x.symbol):
                excel_pool.write_xls_line(
                    ws_name, row, [
                        '', '', '', '', '',
                        'Totale',
                        currency.symbol,
                        (total[currency][0], f_number_bg_blue_bold),
                        currency.symbol,
                        (total[currency][1], f_number_bg_blue_bold),
                        (total[currency][2], f_number_bg_red_bold),
                        ], default_format=f_text_bg_blue)
                row += 1

            # -----------------------------------------------------------------
            # Data:
            # -----------------------------------------------------------------
            # Header:
            excel_pool.write_xls_line(
                ws_name, row, header, default_format=f_header)
            excel_pool.autofilter(ws_name, row, 0, row, len(header) - 1)

            # Record:
            for record, f_text_current in temp_list:
                row += 1
                excel_pool.write_xls_line(
                    ws_name, row, record, default_format=f_text_current)

        # ---------------------------------------------------------------------
        # Docnaet Customer total:
        # ---------------------------------------------------------------------
        ws_name = 'Clienti'
        excel_pool.create_worksheet(name=ws_name)
        width = [
            50, 20,
            3, 12, 12, 12,
            3, 12, 12,
            12, 40,
            ]
        header = [
            'Cliente', 'Nazione',
            'Val.', 'Ordini', 'Offerte', 'Off. perse',
            'Val.', 'Pag. aperti', 'Di cui scaduti',
            'FIDO', 'Note',
            ]
        row = 0

        # Column:
        excel_pool.column_width(ws_name, width)
        excel_pool.freeze_panes(ws_name, 3, 1)

        total = {}
        temp_list = []
        for partner in sorted(partner_total, key=lambda x: x.name):
            # TODO currency?!?
            currency_payment = partner.duelist_currency_id or currency

            first = True
            for currency in partner_total[partner]:
                order, quotation, lost = partner_total[partner][currency]
                # -------------------------------------------------------------
                # Update total in currency mode:
                # -------------------------------------------------------------
                if currency not in total:
                    # order, exposition, deadlined
                    total[currency] = [
                        0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0,
                        ]

                if currency_payment not in total:
                    # order, exposition, deadlined
                    total[currency_payment] = [
                        0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0,
                        ]

                total[currency][0] += order
                # TODO problem if different currency
                total[currency][1] += quotation
                # TODO problem if different currency
                total[currency][2] += lost

                # Payment:
                total[currency_payment][3] += \
                    partner.duelist_exposition_amount or 0.0
                total[currency_payment][4] += \
                    partner.duelist_uncovered_amount or 0.0

                # -------------------------------------------------------------
                # Setup color:
                # -------------------------------------------------------------
                if partner.duelist_uncovered or partner.duelist_over_fido:
                    f_text_current = f_text_red
                    f_number_current = f_number_red
                else:
                    f_text_current = f_text
                    f_number_current = f_number
                if first:
                    first = False
                    temp_list.append(([
                        '%s [%s]' % (
                            partner.name, partner.sql_customer_code or ''),
                        partner.country_id.name if partner.country_id else \
                        'SENZA PAESE',

                        currency.symbol,
                        (order or '', f_number),
                        (quotation or '', f_number),
                        (lost or '', f_number_red),

                        currency_payment.symbol,
                        (partner.duelist_exposition_amount or '',
                            f_number_current),
                        (partner.duelist_uncovered_amount or '',
                            f_number_current),
                        (partner.duelist_fido or '', f_number_current),
                        self.get_partner_note(partner),
                        ], f_text_current))
                else:
                    temp_list.append(([
                            '',

                            currency.symbol,
                            (order or '', f_number),
                            (quotation or '', f_number),
                            (lost or '', f_number_red),

                            # currency_payment.symbol,
                            # (partner.duelist_exposition_amount or '',
                            #     f_number_current),
                            # (partner.duelist_uncovered_amount or '',
                            #     f_number_current),
                            # (partner.duelist_fido or '', f_number_current),
                            # self.get_partner_note(partner),
                            ], f_text_current))

        # ---------------------------------------------------------------------
        # Total page order:
        # ---------------------------------------------------------------------
        for currency in sorted(total, key=lambda x: x.symbol):
            excel_pool.write_xls_line(
                ws_name, row, [
                    '', 'Totale',
                    currency.symbol,
                    (total[currency][0], f_number_bg_blue_bold),
                    (total[currency][1], f_number_bg_blue_bold),
                    (total[currency][2], f_number_bg_red_bold),
                    currency.symbol,
                    (total[currency][3], f_number_bg_blue_bold),
                    (total[currency][4], f_number_bg_red_bold),
                    ], default_format=f_text_bg_blue)
            row += 1

        # ---------------------------------------------------------------------
        # Data:
        # ---------------------------------------------------------------------
        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)
        excel_pool.autofilter(ws_name, row, 0, row, len(header) - 1)

        for record, f_text_current in temp_list:
            row += 1
            excel_pool.write_xls_line(
                ws_name, row, record, default_format=f_text_current)

        # ---------------------------------------------------------------------
        # Docnaet Product total:
        # ---------------------------------------------------------------------
        ws_name = 'Prodotti'
        excel_pool.create_worksheet(name=ws_name)

        width = [12, 30, 2, 10]
        cols = len(month_column)
        width.extend([9 for item in range(0, cols)])
        empty = ['' for item in range(0, cols)]
        if index_today != False:
            empty[index_today] = ('', f_number_bg_blue)

        header = ['Codice', 'Prodotto', 'UM', 'Totale']
        start = len(header)
        header.extend(month_column)

        # Column:
        row = 0
        excel_pool.column_width(ws_name, width)

        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)

        excel_pool.freeze_panes(ws_name, 1, 2)

        uom_total = {}
        for product in sorted(product_total, key=lambda x: x.default_code):
            uom_code = product.uom_id.account_ref or product.uom_id.name

            row += 1
            data = [
                product.default_code,
                product.name,
                uom_code,
                '',
                ]
            data.extend(empty)
            excel_pool.write_xls_line(
                ws_name, row, data,
                default_format=f_text)
            total = 0.0

            for deadline in product_total[product]:
                if deadline == now:
                    f_number_color = f_number_bg_blue
                else:
                    f_number_color = f_number

                subtotal = int(product_total[product][deadline])
                total += subtotal

                # -------------------------------------------------------------
                # Total setup:
                # -------------------------------------------------------------
                if uom_code not in uom_total:
                    uom_total[uom_code] = [0.0 for item in range(0, cols)]
                index = month_column.index(deadline)
                uom_total[uom_code][index] += subtotal

                excel_pool.write_xls_line(
                    ws_name, row, [
                        subtotal,
                        ], default_format=f_number_color, col=start + index)

            excel_pool.write_xls_line(
                ws_name, row, [
                    total,
                    ], default_format=f_number_bg_green_bold, col=start-1)

        # Total Row:
        row += 1

        for uom_code in uom_total:
            excel_pool.write_xls_line(
                ws_name, row, [uom_code, 'Totale:'],
                default_format=f_text,
                col=start - 2)

            excel_pool.write_xls_line(
                ws_name, row, uom_total[uom_code],
                default_format=f_number_bg_green_bold,
                col=start)
            row += 1

        if save_mode:  # Save as a file:
            _logger.info('Save mode: %s' % save_mode)
            return excel_pool.save_file_as(save_mode)
        else:  # Send mail:
            _logger.info('Send mail mode!')
            return excel_pool.send_mail_to_group(
                cr, uid,
                'docnaet_sale_excel.group_sale_statistic_mail',
                'Statistiche vendite',
                'Statistiche giornaliere vendite',
                'sale_statistic.xlsx',
                context=context)

    def extract_sale_excel_account_report(self, cr, uid, context=None):
        """ Schedule extract of sale account report
        """

        if context is None:
            context = {}

        save_mode = context.get('save_mode')
        _logger.info('Start extract save mode: %s' % save_mode)

        # Pool used:
        excel_pool = self.pool.get('excel.writer')
        sale_pool = self.pool.get('sale.order')

        # Collect data:
        now = ('%s' % datetime.now())[:7]
        parameters = {
            'width': 300,
        }
        # ---------------------------------------------------------------------
        # Docnaet Order:
        # ---------------------------------------------------------------------
        ws_name = 'Ordini'
        excel_pool.create_worksheet(name=ws_name)
        width = [
            35, 30, 10,
            8, 8,
            10, 10, 5,
            15,
            ]
        header = [
            'Cliente', 'Destinazione', 'OC',
            'Data', 'Scadenza',
            'Carico', 'Prenotato', 'Preso',
            'Vettore',
            ]
        start_col = len(header)

        sale_ids = sale_pool.search(cr, uid, [
            # ('state', 'in', ('draft', 'sent', 'cancel')),  # todo remove?
            ('accounting_order', '=', True),  # Confirmed order
            ('logistic_state', '!=', 'done'),  # Not closed
            ('partner_id.sql_customer_code', '=ilike', '201%'),
            ], context=context)

        # sale_ids = sale_pool.search(cr, uid, [
        #    ('state', 'in', ('draft', 'sent', 'cancel')),
        #    ('partner_id.sql_customer_code', '=ilike', '201%'),
        #    ], context=context)
        row = 0

        # Format:
        excel_pool.set_format()
        f_title = excel_pool.get_format('title')
        f_header = excel_pool.get_format('header')

        f_text = excel_pool.get_format('text')
        f_text_red = excel_pool.get_format('text_red')
        f_text_bg_blue = excel_pool.get_format('bg_blue')

        f_number = excel_pool.get_format('number')
        f_number_red = excel_pool.get_format('number_red')
        f_number_bg_blue = excel_pool.get_format('bg_blue_number')
        f_number_bg_blue_bold = excel_pool.get_format('bg_blue_number_bold')
        f_number_bg_red_bold = excel_pool.get_format('bg_red_number_bold')
        f_number_bg_green_bold = excel_pool.get_format('bg_green_number_bold')

        # Column:
        excel_pool.column_width(ws_name, width)

        # ---------------------------------------------------------------------
        # Data:
        # ---------------------------------------------------------------------
        row = 0

        # Header:
        excel_pool.write_xls_line(
            ws_name, row, header, default_format=f_header)
        header_row = row

        sale_proxy = sale_pool.browse(cr, uid, sale_ids, context=context)

        product_total = {}  # Statistic for product (uom distinct)
        max_product = 0  # For print headers after

        for order in sorted(
                sale_proxy,
                key=lambda x: (x.partner_id.name, x.name)
                ):
            row += 1
            partner = order.partner_id

            # -----------------------------------------------------------------
            # Excel Header data:
            # -----------------------------------------------------------------
            # Setup color:
            if partner.duelist_uncovered or partner.duelist_over_fido:
                f_text_current = f_text_red
                f_number_current = f_number_red
            else:
                f_text_current = f_text
                f_number_current = f_number

            deadline = order.date_deadline or ''
            excel_pool.write_xls_line(ws_name, row, [
                '%s [%s]' % (
                    partner.name, partner.sql_customer_code or ''),
                '',  # TODO destination
                order.name,
                order.date_order,
                deadline,

                # 'Carico', 'Prenotato', 'Preso', 'Vettore',
                '', '', '', '',  # TODO get this data?

                # (partner.duelist_exposition_amount or '', f_number_current),
                # (partner.duelist_uncovered_amount or '', f_number_current),
                # (partner.duelist_fido or '', f_number_current),
                # self.get_partner_note(partner),
                ], default_format=f_text_current)

            # -----------------------------------------------------------------
            # Line data:
            # -----------------------------------------------------------------
            col = start_col

            total_product = 0
            for line in order.order_line:
                if line.logistic_state in ('done', 'cancel'):
                    continue  # Remove line yet delivered (r cancel - need?)

                product = line.product_id
                if not product:
                    continue

                line_deadline = line.date_deadline
                uom_id = product.uom_id
                qty = line.product_uom_qty
                if uom_id not in product_total:
                    product_total[uom_id] = 0.0
                product_total[uom_id] += qty

                excel_pool.write_xls_line(ws_name, row, [
                    (qty, f_number_current),
                    product.default_code or product.name,
                    ], col=col, default_format=f_text_current)

                # Comment for different deadline:
                if line_deadline and line_deadline != deadline:
                    excel_pool.write_comment(
                        ws_name,
                        row, col,
                        'Consegnare: %s' % line_deadline,
                        # parameters,
                    )

                total_product += 1
                if total_product > max_product:
                    max_product = total_product
                col += 2  # data line column are 2!

        # ---------------------------------------------------------------------
        # Total page order:
        # ---------------------------------------------------------------------
        row += 2
        for uom_id in sorted(product_total, key=lambda x: x.name):
            excel_pool.write_xls_line(
                ws_name, row, [
                    'Totale %s' % uom_id.name,
                    (product_total[uom_id], f_number_bg_blue_bold),
                    ], default_format=f_text_bg_blue)
            row += 1

        # TODO write header extra data
        header_line = ['Q.', 'Prodotto']
        for loop in range(max_product):
            this_col = loop * 2 + start_col
            excel_pool.write_xls_line(
                # TODO write in header row!
                ws_name, header_row, header_line,
                col=this_col, default_format=f_header)
            excel_pool.column_width(ws_name, [10, 15], col=this_col)
        if max_product:
            excel_pool.autofilter(
                ws_name, header_row, 0, header_row,
                (loop + 1) * 2 + start_col - 1)

        excel_pool.freeze_panes(ws_name, header_row + 1, 1)

        if save_mode:  # Save as a file:
            _logger.info('Save mode: %s' % save_mode)
            return excel_pool.save_file_as(save_mode)
        else:  # Send mail:
            _logger.info('Send mail mode!')
            return excel_pool.send_mail_to_group(
                cr, uid,
                'docnaet_sale_excel.group_sale_statistic_mail',
                'Statistiche contabilità',
                'Statistiche giornaliere contabili',
                'sale_statistic_accounting.xlsx',
                context=context)
