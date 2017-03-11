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
import openerp.netsvc as netsvc
from openerp.osv import osv, orm, fields
from datetime import datetime, timedelta
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

# TODO res.country (importabili con i partner)
class ResCompany(orm.Model):
    ''' Docnaet company extra fields
    '''
    _inherit = 'res.company'
    
    def get_docnaet_folder_path(self, cr, uid, subfolder='root', context=None):
        ''' Function for get (or create) root docnaet folder 
            (also create extra subfolder)
            subfolder: string value for sub root folder, valid value:
                > 'store'
                > 'private'
        '''
        # Get docnaet path from company element
        company_ids = self.search(cr, uid, [], context=context)
        company_proxy = self.browse(cr, uid, company_ids, context=context)[0]
        docnaet_path = company_proxy.docnaet_path
        
        # Folder structure:
        path = {}
        path['root'] = docnaet_path
        path['store'] = os.path.join(docnaet_path, 'store')
        path['private'] = os.path.join(docnaet_path, 'private')
        path['user'] = os.path.join(path['private'], str(uid))
        
        # Create folder structure # TODO test if present
        for folder in path:
            if not os.path.isdir(path[folder]):
                os.system('mkdir -p %s' % path[folder])        
        return path[subfolder]

    def assign_fax_fax(self, cr, uid, context=None):
        ''' Assign protocol and update number in record
        '''
        company_id = self.search(cr, uid, [], context=context)[0] # TODO
        
        
        company_proxy = self.browse(cr, uid, company_id, context=context)
        number = company_proxy.next_fax
        self.write(cr, uid, company_id, {
            'next_fax': number + 1,
            }, context=context)
        return number
        
    _columns = {
        'docnaet_path': fields.char(
            'Docnaet path', size=64, required=True,
            help='Docnaet root path in file system for store docs'), 
        'next_fax': fields.integer('Next fax number'),
        }

class DocnaetLanguage(orm.Model):
    ''' Object docnaet.language
    '''    
    _name = 'docnaet.language'
    _description = 'Docnaet language'
    _order = 'name'
                    
    _columns = {        
        'name': fields.char('Language', size=64, required=True),
        'code': fields.char('Code', size=16),
        'iso_code': fields.char('ISO Code', size=16),
        'note': fields.text('Note'),
        }

class DocnaetType(orm.Model):
    ''' Object docnaet.type
    '''    
    _name = 'docnaet.type'
    _description = 'Docnaet type'
    _order = 'name'
    

    _columns = {        
        'name': fields.char('Type', size=64, required=True),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' Object docnaet.protocol
    '''    
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'
    _order = 'name'

    def assign_protocol_number(self, cr, uid, protocol_id, context=None):
        ''' Assign protocol and update number in record
        '''
        protocol_proxy = self.browse(cr, uid, protocol_id, context=context)
        number = protocol_proxy.next
        self.write(cr, uid, protocol_id, {
            'next': number + 1,
            }, context=context)
        return number
        
    _columns = {        
        'name': fields.char('Protocol', size=64, required=True),
        'next': fields.integer('Next protocol', required=True), 
        'note': fields.text('Note'),
        # TODO default_application_id
        }
    _defaults = {
        'next': lambda *x: 1,
        }    

class DocnaetProtocolTemplateProgram(orm.Model):
    ''' Object docnaet.protocol.template.program
    '''    
    
    _name = 'docnaet.protocol.template.program'
    _description = 'Docnaet program'
    _order = 'name'
                   
    def get_program_from_extension(self, cr, uid, extension, context=None):
        ''' Return program ID from extension
        ''' 
        program_ids = self.search(cr, uid, [
            ('extension', 'ilike', extension)
            ], context=context)
            
        if program_ids:
            return program_ids[0]
        else: 
            return False
            
    _columns = {        
        'name': fields.char('Program', size=64, required=True),
        'extension': fields.char('Extension', size=5),
        'note': fields.text('Note'),
        }

class DocnaetProtocolTemplate(orm.Model):
    ''' Object docnaet.protocol.template
    '''    
    
    _name = 'docnaet.protocol.template'
    _description = 'Docnaet protocol template'
    _rec_name = 'lang_id'
    _order = 'lang_id'

    _columns = {
        'lang_id': fields.many2one('docnaet.language', 'Language', 
            required=True),
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol'),
        'program_id': fields.many2one('docnaet.protocol.template.program', 
            'Program'),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' 2many fields
    '''    
    _inherit = 'docnaet.protocol'

    _columns = {
        'template_ids': fields.one2many('docnaet.protocol.template', 
            'protocol_id', 'Template'),
        }

class DocnaetDocument(orm.Model):
    ''' Object docnaet.document
    '''    
    _name = 'docnaet.document'
    _description = 'Docnaet document'
    _order = 'date desc,name'
        
    # -------------------------------------------------------------------------
    # Workflow state event: 
    # -------------------------------------------------------------------------
    def document_draft(self, cr, uid, ids, context=None):
        ''' WF draft state
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        self.write(cr, uid, ids, {
            'state': 'draft',
            }, context=context)
        return True

    def document_confirmed(self, cr, uid, ids, context=None):
        ''' WF confirmed state
        '''        
        assert len(ids) == 1, 'Works only with one record a time'
        data = {'state': 'confirmed'}
        
        protocol_pool = self.pool.get('docnaet.protocol')
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        if not current_proxy.number:
            protocol = current_proxy.protocol_id
            if not protocol:
                raise osv.except_osv(
                    _('Protocol'), 
                    _('No protocol assigned, choose one before and confirm!'),
                    )
            data['number'] = protocol_pool.assign_protocol_number(
                cr, uid, protocol.id, context=context)
        return self.write(cr, uid, ids, data, context=context)

    def document_suspended(self, cr, uid, ids, context=None):
        ''' WF suspended state
        '''
        data = {'state': 'suspended'}
        return self.write(cr, uid, ids, data, context=context)

    def document_timed(self, cr, uid, ids, context=None):
        ''' WF timed state
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        data = {'state': 'timed'}
        
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        if not current_proxy.deadline:
            raise osv.except_osv(
                _('Timed document'), 
                _('For timed document need a deadline!'),
                )
        return self.write(cr, uid, ids, data, context=context)

    def document_cancel(self, cr, uid, ids, context=None):
        ''' WF cancel state
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        data = {'state': 'cancel'}
        return self.write(cr, uid, ids, data, context=context)

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def call_docnaet_url(self, cr, uid, ids, mode, context=None):    
        ''' Call url in format: docnaet://operation|argument 
            Cases:
            document|document_id.extension > open document
            folder|uid > open personal folder (for updload document)
            
            NOTE: maybe expand the services
        '''        
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]

        if mode == 'open':  # TODO rimettere id e togliere docnae_id
            final_url = r'docnaet://document|%s.%s' % (
                doc_proxy.id,
                #doc_proxy.docnaet_id \
                #    if not doc_proxy.original_id \
                #    else doc_proxy.original_id.id,
                doc_proxy.docnaet_extension or 'doc', # default doc
                )
        elif mode == 'home':
            final_url = r'docnaet://folder|%s' % uid

        return {
            'name': 'Docnaet document',
            #res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url', 
            'url': final_url, 
            'target': 'new', # self
            }

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def button_assign_fax_number(self, cr, uid, ids, context=None):
        ''' Assign fax number to document (next counter)
        '''
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        if current_proxy.fax_number:
            raise osv.except_osv(
                _('Fax error'), 
                _('Fax yet present!'),
                )
        number = self.pool.get('res.company').assign_fax_fax(
            cr, uid, context=context)
        return self.write(cr, uid, ids, {
            'fax_number': number,
            }, context=context)

    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call url function for prepare address and return for open doc:
        '''
        return self.call_docnaet_url(cr, uid, ids, 'open', context=context)
                       
    _columns = {        
        'name': fields.char('Subject', size=80, required=True),
        'filename': fields.char('File name', size=200),
        'description': fields.text('Description'),
        'note': fields.text('Note'),
        
        'number': fields.char('N.', size=10),
        'fax_number': fields.char('Fax n.', size=10),

        'date': fields.date('Date', required=True),
        'deadline': fields.date('Deadline'),
        'deadline_info': fields.char('Deadline info', size=64),

        # OpenERP many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol', 
            #required=True
            ),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'type_id': fields.many2one('docnaet.type', 'Type'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'docnaet_extension': fields.char('Ext.', size=10),
        'program_id': fields.many2one(
            'docnaet.protocol.template.program', 'Type of document'),

        'original_id': fields.many2one('docnaet.document', 'Original',
            help='Parent orignal document after this duplication'),
        'imported': fields.boolean('Imported'), 
        'private': fields.boolean('Private'), 
        # Workflow date event:
        #'date_confirmed': fields.text('Confirmed event', required=True),
        #'date_suspended': fields.date('Suspended event', required=True),
        #'date_deadline': fields.date('Deadline event', required=True),

        'priority': fields.selection([
            ('lowest', 'Lowest'),
            ('low', 'Low'),
            ('normal', 'Normal'),
            ('high', 'high'),
            ('highest', 'Highest'), ], 'Priority'),
        
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('suspended', 'Suspended'),
            ('timed', 'Timed'),
            ('cancel', 'Cancel'), ], 'State', readonly=True),
        }
        
    _defaults = {
        'date': lambda *x: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
        'priority': lambda *x: 'normal',
        'state': lambda *x: 'draft',        
        }    

class DocnaetDocument(orm.Model):
    ''' Add extra relation fileds
    '''          
    _inherit = 'docnaet.document'

    _columns = {
        'duplicated_ids': fields.one2many('docnaet.document', 'original_id',
            'duplicated', help='Child document duplicated from this'),
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
