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
            
        # Pool used:
        document_pool = self.pool.get('docnaet.document')

        # Record data management:
        original_id = context.get('active_id')
        original_proxy = document_pool.browse(    
            cr, uid, original_id, context=context)
        data = {
            'name': original_proxy.name,             
            'description': original_proxy.description,
            'note': original_proxy.note,            
            'number': False,
            'fax_number': False,
            'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
            'deadline': False,
            'deadline_info': False,
            'protocol_id': original_proxy.protocol_id.id,
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
            }
        if mode == 'link':
            # link document
            data['original_id'] = original_id # so document stay here!

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
        
        return {
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'res_model': 'docnaet.document',
            #'domain': [('id', '=', destination_id)],
            'type': 'ir.actions.act_window',
            'res_id': destination_id,  # IDs selected
            }

    def duplication_document(self, cr, uid, ids, context=None):
        ''' Duplicate document and file
        '''
        return self.duplicate_operation(
            cr, uid, ids, mode='document', context=context)
        
    def linked_document(self, cr, uid, ids, context=None):
        ''' Duplicate record but not file
        '''
        return self.duplicate_operation(
            cr, uid, ids, mode='link', context=context)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
