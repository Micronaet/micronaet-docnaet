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

class document_duplication(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _name = 'docnaet.document.duplication.wizard'
    _description = 'Document duplication'

    def duplicate_operation(self, cr, uid, ids, mode='link', context=None):
        ''' Manage 2 case
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        if context is None:
            raise osv.except_osv(
                _('ID error'), 
                _('Cannot found original document'),
                )
            
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
            
        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        
        #with_number = context.get('with_number', False)
        linked_document = context.get('linked_document', False)
        
        # Record data management:
        original_id = context.get('active_id')
        original_proxy = document_pool.browse(    
            cr, uid, original_id, context=context)
        reassign_protocol = True if wiz_proxy.protocol_id else False
        protocol_id = \
            wiz_proxy.protocol_id.id or original_proxy.protocol_id.id or False
            
        data = {
            'name': original_proxy.name,             
            'description': original_proxy.description,
            'note': original_proxy.note,            
            #'number': False,
            #'fax_number': False,
            'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
            'deadline': False,
            'deadline_info': False,
            'protocol_id': protocol_id,
            'language_id': original_proxy.language_id.id,
            'type_id': original_proxy.type_id.id,
            'company_id': original_proxy.company_id.id,
            'user_id': uid,
            'partner_id': original_proxy.partner_id.id,
            'docnaet_extension': original_proxy.docnaet_extension,
            'program_id': original_proxy.program_id.id,
            'priority': original_proxy.priority,        
            'state': 'draft',
            # XXX remember when add new fields to update this record!
            'original_id': original_id if mode == 'link' else False,
            }
        # Manage protocol number (3 cases):
        if reassign_protocol or not linked_document: # always if reassigned 
            data['number'] = protocol_pool.assign_protocol_number(
                cr, uid, protocol_id, context=context)
        elif linked_document: # linked not reassigned keep the number
            data['number'] = original_proxy.number or False
        else:
            data['number'] = False
            
        destination_id = document_pool.create(cr, uid, data, context=context)
        destination_proxy = document_pool.browse(    
            cr, uid, destination_id, context=context)
        
        # File management:
        if mode != 'link': 
            # duplicate also file:
            original_file = document_pool.get_document_filename(
                cr, uid, original_proxy, mode='fullname', context=context)
            destination_file = document_pool.get_document_filename(
                cr, uid, destination_proxy, mode='fullname', context=context)            
            shutil.copyfile(original_file, destination_file)
            try:            
                os.system('chown openerp7:openerp7 %s' % destination_file)
                os.system('chmod 775 %s' % destination_file)
                _logger.info('Change permission to new file')
            except:
                _logger.error('Cannot set property of file')            
        
        return {
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'res_model': 'docnaet.document',
            #'domain': [('id', '=', destination_id)],
            'domain': [
                '|',
                ('state','!=','draft'),
                '&',
                ('user_id','=',uid),
                ('state','=','draft'),
                ],
            'type': 'ir.actions.act_window',
            'res_id': destination_id,  # IDs selected
            }

    def duplication_document(self, cr, uid, ids, context=None):
        ''' Duplicate document and file
        '''
        if context is None:
            context = {}

        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        #context['with_number'] = current_proxy.with_number
        return self.duplicate_operation(
            cr, uid, ids, mode='document', context=context)
        
    def linked_document(self, cr, uid, ids, context=None):
        ''' Duplicate record but not file
        '''
        if context is None:
            context = {}

        context['linked_document'] = True
        return self.duplicate_operation(
            cr, uid, ids, mode='link', context=context)
    
    _columns = {
        # To remove
        #'with_number': fields.boolean('With number'),
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol'),
        }
    
    _defaults = {
        #'with_number': lambda *x: False,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
