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
    ''' Wizard for duplicate model
    '''
    _name = 'docnaet.document.advanced.search.wizard'
    _description = 'Advanced search'

    def onchange_country_partner_domain(self, cr, uid, ids, partner_name,
            country_id, category_id, context=None):
        ''' On change for domain purpose
        '''    
        res = {}
        res['domain'] = {'partner_id': [
            ('docnaet_enable','=',True),
            ]}        
        
        if country_id:
            res['domain']['partner_id'].append(
                ('country_id','=',country_id),
                )
        if partner_name:
            res['domain']['partner_id'].append(
                ('name','ilike',partner_name),
                )
        if category_id:
            res['domain']['partner_id'].append(
                ('docnaet_category_id','=', category_id),
                )
        return res
    
    def advanced_search(self, cr, uid, ids, context=None):
        ''' Advanced search
        '''
        assert len(ids) == 1, 'Works only with one record a time'
            
        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        domain = []
        keywords = current_proxy.keywords or False
        partner_name = current_proxy.partner_name or False
        protocol_id = current_proxy.protocol_id.id or False
        partner_id = current_proxy.partner_id.id or False
        country_id = current_proxy.country_id.id or False
        from_date = current_proxy.from_date
        to_date = current_proxy.to_date
        from_deadline = current_proxy.from_deadline
        to_deadline = current_proxy.to_deadline
        
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
        
        if partner_name:
            domain.append(('partner_id.name', 'ilike', partner_name))
        if protocol_id:
            domain.append(('protocol_id', '=', protocol_id))
        if country_id:
            domain.append(('country_id', '=', country_id))
        if partner_id:
            domain.append(('partner_id', '=', partner_id))            

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

        if keywords:
            # TODO manage multi fields
            #if not domain:
            #    domain.append('&')
                
            for key in keywords.split(): 
                domain.append(('name', 'ilike', key))      
                
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': domain,
            'type': 'ir.actions.act_window',
            #'res_id': destination_id,  # IDs selected
            }

    _columns = {
        'keywords': fields.char('Keywords', size=80),
        'partner_name': fields.char('Partner name', size=80),
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol',
            domain=[('invisible', '=', False)]),
        'partner_id': fields.many2one('res.partner', 'Partner'),
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
        'priority': fields.selection([
            ('lowest', 'Lowest'),
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'high'),
            ('highest', 'Highest'), 
            ], 'Priority'),
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
