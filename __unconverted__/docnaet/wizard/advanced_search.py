# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP)
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
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
import shutil
from openerp.osv import osv, orm, fields
from datetime import datetime
from datetime import datetime, timedelta
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    DATETIME_FORMATS_MAP,
    float_compare)

_logger = logging.getLogger(__name__)


class docnaet_document_advanced_search_wizard(orm.TransientModel):
    """ Wizard for duplicate model
    """
    _name = 'docnaet.document.advanced.search.wizard'
    _description = 'Advanced search'

    def onchange_country_partner_domain(
            self, cr, uid, ids, partner_name,
            country_id, category_id, context=None):
        """ On change for domain purpose
        """
        partner_pool = self.pool.get('res.partner')
        res = {}
        res['domain'] = {'partner_id': [
            ('docnaet_enable', '=', True),
            ]}

        if partner_name:
            res['domain']['partner_id'].extend([
                ('name', 'ilike', partner_name)
                ])
            """    
            domain = [
                '|',
                ('name', 'ilike', partner_name),
                ('alternative_search', 'ilike', partner_name),
                ]     
            partner_ids = partner_pool.search(cr, uid, domain, context=context)  
            res['domain']['partner_id'].append(
                ('id', 'in', partner_ids))
            """

        if country_id:
            res['domain']['partner_id'].extend([
                ('country_id', '=', country_id)
                ])
        if category_id:
            res['domain']['partner_id'].extend([
                ('docnaet_category_id', '=', category_id)
                ])

        _logger.error('DOMAIN: %s' % (res, ))
        return res

    def advanced_search(self, cr, uid, ids, context=None):
        """ Advanced search
        """
        assert len(ids) == 1, 'Works only with one record a time'

        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        parent_pool = self.pool.get('res.partner')

        current_proxy = self.browse(cr, uid, ids, context=context)[0]

        docnaet_mode = current_proxy.docnaet_mode or 'docnaet'

        keywords = current_proxy.keywords or False
        partner_name = current_proxy.partner_name or False
        protocol_id = current_proxy.protocol_id.id or False
        sector_id = current_proxy.sector_id.id or False
        partner_id = current_proxy.partner_id.id or False
        country_id = current_proxy.country_id.id or False
        from_date = current_proxy.from_date
        to_date = current_proxy.to_date
        from_deadline = current_proxy.from_deadline
        to_deadline = current_proxy.to_deadline

        # Labnaet:
        product_id = current_proxy.product_id.id or False
        docnaet_product_category_id = \
            current_proxy.docnaet_product_category_id.id or False

        name = current_proxy.name
        number = current_proxy.number
        user_id = current_proxy.user_id.id or False
        description = current_proxy.description
        note = current_proxy.note
        type_id = current_proxy.type_id.id or False
        language_id = current_proxy.language_id.id or False
        program_id = current_proxy.program_id.id or False
        docnaet_extension = current_proxy.docnaet_extension
        priority = current_proxy.priority
        docnaet_category_id = current_proxy.docnaet_category_id.id or False

        domain = [('docnaet_mode', '=', docnaet_mode)]

        if partner_name:
            # Search partner name in partner but also in parent name:
            partner_ids = parent_pool.search(cr, uid, [
                '|',
                ('name', 'ilike', partner_name),
                ('docnaet_parent_id.name', 'ilike', partner_name),
                ], context=context)
            domain.append(('partner_id', 'in', partner_ids))

        if partner_id:
            # Search partner name in partner but also in parent id:
            partner_ids = parent_pool.search(cr, uid, [
                ('docnaet_parent_id', '=', partner_id),
                ], context=context)
            partner_ids.append(partner_id)
            domain.append(('partner_id', 'in', partner_ids))

        if sector_id:
            domain.append(('sector_id', '=', sector_id))
        if protocol_id:
            domain.append(('protocol_id', '=', protocol_id))
        if country_id:
            domain.append(('country_id', '=', country_id))

        # Labnaet:
        if product_id:
            domain.append(('product_id', '=', product_id))
        if docnaet_product_category_id:
            domain.append(
                ('docnaet_product_category_id', '=',
                    docnaet_product_category_id))

        if from_date:
            domain.append(('date', '>=', from_date))
        if to_date:
            domain.append(('date', '<=', from_date))

        if from_deadline:
            domain.append(('deadline', '>=', from_deadline))
        if to_deadline:
            domain.append(('deadline', '<=', to_deadline))

        if name:
            domain.append(('name', 'ilike', name))
        if number:
            domain.append(('number', 'ilike', number))
        if user_id:
            domain.append(('user_id', '=', user_id))
        if description:
            domain.append(('description', 'ilike', description))
        if note:
            domain.append(('note', 'ilike', note))
        if type_id:
            domain.append(('type_id', '=', type_id))
        if language_id:
            domain.append(('language_id', '=', language_id))
        if program_id:
            domain.append(('program_id', '=', program_id))
        if docnaet_extension:
            domain.append(('docnaet_extension', 'ilike', docnaet_extension))
        if priority:
            domain.append(('priority', '=', priority))
        if docnaet_category_id:
            domain.append(('docnaet_category_id', '=', docnaet_category_id))

        # Multi search management of splitted keywords:
        if keywords:
            set_ids = {}
            for field in ('name', 'note', 'description'):
                kw_domain = []
                for key in keywords.split():
                    kw_domain.append((field, 'ilike', key))
                set_ids[field] = set(document_pool.search(
                    cr, uid, kw_domain, context=context))
            keyword_ids = list(
                set_ids['name'] | set_ids['note'] | set_ids['description'])
            domain.append(('id', 'in', keyword_ids))

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': domain,
            'type': 'ir.actions.act_window',
            #'res_id': destination_id,  # IDs selected
            'context': context,
            }

    _columns = {
        'keywords': fields.char('Keywords', size=80),
        'partner_name': fields.char('Partner name', size=80),
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol',
            domain=[('invisible', '=', False)]),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'sector_id': fields.many2one('docnaet.sector', 'Settore'),
        # 'docnaet_parent_id': fields.many2one('res.partner', 'Parent partner')
        'country_id': fields.many2one('res.country', 'Country'),
        'from_date': fields.date('From date'),
        'to_date': fields.date('To date'),
        'from_deadline': fields.date('From deadline'),
        'to_deadline': fields.date('To deadline'),
        'name': fields.char('Subject', size=180),
        'user_id': fields.many2one('res.users', 'User'),
        'description': fields.char('Description', size=180,),
        'note': fields.char('Note', size=180,),
        'type_id': fields.many2one('docnaet.type', 'Type',
            domain=[('invisible', '=', False)]),
        'number': fields.char('N.', size=10),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'program_id': fields.many2one(
            'docnaet.protocol.template.program', 'Type of document'),
        'docnaet_extension': fields.char('Ext.', size=10),
        'docnaet_category_id': fields.many2one(
            'res.partner.docnaet', 'Partner category',
            ),
        # Labnaet:
        'product_id': fields.many2one(
            'docnaet.product', 'Product'),
        'docnaet_product_category_id': fields.many2one(
            'product.product.docnaet', 'Product category',
            ),

        'priority': fields.selection([
            ('lowest', 'Lowest'),
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'high'),
            ('highest', 'Highest'),
            ], 'Priority'),
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            #('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }

    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
