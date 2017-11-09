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
        'name': fields.char('Language', size=64, required=True,
            translate=True),
        'code': fields.char('Code', size=16),
        'iso_code': fields.char('ISO Code', size=16),
        'note': fields.text('Note'),
        }

class ResPartnerDocnaet(orm.Model):
    ''' Object res.partner.docnaet
    '''    
    _name = 'res.partner.docnaet'
    _description = 'Partner category'
                    
    _columns = {        
        'name': fields.char('Docnaet type', size=64, required=True,
            translate=True),
        'note': fields.text('Note'),
        }

class ResPartner(orm.Model):
    """ Model name: ResPartner
    """    
    _inherit = 'res.partner'
    
    def set_docnaet_on(self, cr, uid, ids, context=None):
        ''' Enalble docnaet partner
        '''
        return self.write(cr, uid, ids, {
            'docnaet_enable': True,
            }, context=context)

    def set_docnaet_off(self, cr, uid, ids, context=None):
        ''' Disalble docnaet partner
        '''
        return self.write(cr, uid, ids, {
            'docnaet_enable': False,
            }, context=context)
            
    _columns = {
        'docnaet_enable': fields.boolean('Docnaet partner'),
        'docnaet_category_id': fields.many2one(
            'res.partner.docnaet', 'Docnaet category'),
        }

class DocnaetType(orm.Model):
    ''' Object docnaet.type
    '''    
    _name = 'docnaet.type'
    _description = 'Docnaet type'
    _order = 'name'
    
    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def set_invisibile(self, cr, uid, ids, context=None):
        ''' Set as invisible protocol
        '''
        return self.write(cr, uid, ids, {
            'invisible': True,            
            }, context=context)
            
    def set_visibile(self, cr, uid, ids, context=None):
        ''' Set as invisible protocol
        '''
        return self.write(cr, uid, ids, {
            'invisible': False,
            }, context=context)

    _columns = {        
        'name': fields.char('Type', size=64, required=True, translate=True),
        'invisible': fields.boolean('Not used'),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' Object docnaet.protocol
    '''    
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'
    _order = 'name'

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def set_invisibile(self, cr, uid, ids, context=None):
        ''' Set as invisible protocol
        '''
        return self.write(cr, uid, ids, {
            'invisible': True,            
            }, context=context)
            
    def set_visibile(self, cr, uid, ids, context=None):
        ''' Set as invisible protocol
        '''
        return self.write(cr, uid, ids, {
            'invisible': False,
            }, context=context)
            
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
        'name': fields.char('Protocol', size=64, required=True,
            translate=True),
        'next': fields.integer('Next protocol', required=True), 
        'note': fields.text('Note', translate=True),
        # TODO default_application_id
        'invisible': fields.boolean('Not used'),
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
        'name': fields.char('Program', size=64, required=True, translate=True),
        'extension': fields.char('Extension', size=5),
        'note': fields.text('Note', translate=True),
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
    _order = 'date desc,number desc'

    # -------------------------------------------------------------------------        
    # Override ORM
    # -------------------------------------------------------------------------
    '''def search(self, cr, user, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        """
        Override search ORM method splitting name if there's * char in it, es.:
        searching: "name1*name2" = search name ilike name1 and name ilike name2 
    
        @param cr: cursor to database
        @param user: id of current user
        @param args: list of conditions to be applied in search opertion
        @param offset: default from first record, you can start from n records
        @param limit: # of records to be comes in answer from search opertion
        @param order: ordering on any field(s)
        @param context: context arguments, like lang, time zone
        @param count: 
        @return: a list of integers based on search domain
        """
        split_element = "*" # TODO parametrize for set up in a view!
        
        new_args = []
        for search_item in args:
            if len(search_item) == 3 and search_item[0] == 'name':
                multi_search = search_item[2].split(split_element)
                if multi_search > 1:
                    total_split = len(multi_search)
                    for i in range(0, total_split):
                        if i != total_split - 1:
                            new_args.append("&")
                        new_args.append(('name', 'ilike', multi_search[i]))                    
                else:
                    new_args.append(search_item)
            else:
                new_args.append(search_item)
        return super(product_product_override_search, self).search(
            cr, user, new_args, offset, limit, order, context, count)'''
    
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
            if not current_proxy.partner_id:
                raise osv.except_osv(
                    _('Partner'), 
                    _('No partner assigned, choose one before and confirm!'),
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
    def dummy(self, cr, uid, ids, context=None):
        return True
        
    def call_docnaet_url(self, cr, uid, ids, mode, remote=False, context=None):    
        ''' Call url in format: openerp://operation|argument 
            Cases:
            document|document_id.extension > open document
            folder|uid > open personal folder (for updload document)
            
            NOTE: maybe expand the services
        '''        
        #handle = 'docnaet' # put in company
        handle = 'openerp' # put in company
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]

        if mode == 'open':  # TODO rimettere id e togliere docnaet_id
            filename = self.get_document_filename(
                cr, uid, doc_proxy, mode='filename', context=context)
            final_url = r'%s://document|%s' % (
                handle, filename)
        elif mode == 'home':
            final_url = r'%s://folder|%s' % (
                handle, uid)
        if remote:
            final_url = '%s[R]' % final_url

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
    def assign_protocol_number(self, cr, uid, ids, context=None):
        ''' Reassign protocol number (enabled only if protocol and number
            is present (in view)
            Used also for N records
        '''
        for document in self.browse(cr, uid, ids, context=context):        
            number = self.pool.get('docnaet.protocol').assign_protocol_number(
                cr, uid, document.protocol_id.id, context=context)
            self.write(cr, uid, document.id, {
                'number': number,
                }, context=context)
        return True                

    def button_doc_info_docnaet(self, cr, uid, ids, context=None):
        ''' Document info
        '''
        assert len(ids) == 1, 'Works only with one record a time'
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        filename = self.get_document_filename(
            cr, uid, current_proxy, mode='fullname', context=context)
        message = _(
            'ID: %s\nOrigin ID: %s\nExtension: %s\nOld filename: %s\nDocument: %s') % (
                current_proxy.id,
                current_proxy.original_id.id if \
                    current_proxy.original_id else '',
                current_proxy.docnaet_extension or '',
                current_proxy.filename or '',
                filename or '',
                )
             
        raise osv.except_osv(
            _('Document info'), 
            message,
            )
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
    
    def button_call_url_remote_docnaet(self, cr, uid, ids, context=None):
        ''' Call url function for prepare address and return for open doc:
            (in remote mode)
        '''
        return self.call_docnaet_url(
            cr, uid, ids, 'open', remote=True, context=context)

    def get_document_filename(
            self, cr, uid, document, mode='fullname', context=None):
        ''' Recursive function for get filename        
            document: browse obj
            mode: fullname or filename only
        '''
        company_pool = self.pool.get('res.company')
        if document.filename:
            store_folder = company_pool.get_docnaet_folder_path(
                cr, uid, subfolder='store', context=context)
            filename = '%s.%s' % (
                document.filename, 
                document.docnaet_extension,
                )
            if mode == 'filename':
               return filename
            else: #fullname:
               return os.path.join(store_folder, filename)
        elif document.original_id:
            return self.get_document_filename(
                cr, uid, document.original_id, mode=mode, context=context)
        else: # Duplicate also file:
            store_folder = company_pool.get_docnaet_folder_path(
                cr, uid, subfolder='store', context=context)
            filename = '%s.%s' % (document.id, document.docnaet_extension)
            if mode == 'filename':
                return filename
            else:# fullname mode:
                return os.path.join(store_folder, filename)

    def _refresh_partner_country_change(self, cr, uid, ids, context=None):
        ''' When change partner in country change in document
        '''        
        return self.pool.get('docnaet.document').search(cr, uid, [
            ('partner_id', 'in', ids)], context=context)

    def _refresh_partner_category_change(self, cr, uid, ids, context=None):
        ''' When change partner in category change in document
        '''        
        return self.pool.get('docnaet.document').search(cr, uid, [
            ('partner_id', 'in', ids)], context=context)

    def _refresh_category_auto_change(self, cr, uid, ids, context=None):
        ''' When change partner in category change in document
        '''        
        return ids

    def _refresh_country_auto_change(self, cr, uid, ids, context=None):
        ''' When change partner in category change in document
        '''        
        return ids

    def _get_real_filename(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = item.filename or item.original_id.id or ''
        return res

    def _get_date_month_4_group(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for doc in self.browse(cr, uid, ids, context=context):
            if doc.date:
                res[doc.id] = ('%s' % doc.date)[:7]
            else:
                res[doc.id] = _('Non presente')
        return res

    def _get_deadline_month_4_group(self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for doc in self.browse(cr, uid, ids, context=context):
            if doc.deadline:
                res[doc.id] = ('%s' % doc.deadline)[:7]
            else:
                res[doc.id] = _('Non presente')
        return res
    
    def _store_data_deadline_month(self, cr, uid, ids, context=None):
        ''' if change date reload data
        '''
        _logger.warning('Change date_mont depend on date and deadline')
        return ids
    
        
    _columns = {        
        'name': fields.char('Subject', size=180, required=True),
        'filename': fields.char('File name', size=200),
        'real_file': fields.function(
            _get_real_filename, method=True, size=20,
            type='char', string='Real filename', store=False), 
        'description': fields.text('Description'),
        'note': fields.text('Note'),
        
        'number': fields.char('N.', size=10),
        'fax_number': fields.char('Fax n.', size=10),

        'date': fields.date('Date', required=True),
        'date_month': fields.function(
            _get_date_month_4_group, method=True, 
            type='char', string='Mese inser.', size=7, 
            store={
                'docnaet.document': (
                    _store_data_deadline_month, ['date'], 10),
                }), 
                        
        'deadline_info': fields.char('Deadline info', size=64),
        'deadline': fields.date('Deadline'),
        'deadline_month': fields.function(
            _get_deadline_month_4_group, method=True, 
            type='char', string='Scadenza', size=7, 
            store={
                'docnaet.document': (
                    _store_data_deadline_month, ['deadline'], 10),
                }), 

        # OpenERP many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol', 
            domain=[('invisible', '=', False)], #required=True
            ),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'type_id': fields.many2one('docnaet.type', 'Type', 
            domain=[('invisible', '=', False)]),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'country_id': fields.related(
            'partner_id', 'country_id', type='many2one', 
            relation='res.country', string='Country',
            store={
                'res.partner': (
                    _refresh_partner_country_change, ['country_id'], 10),
                'docnaet.document': (
                    _refresh_country_auto_change, ['partner_id'], 10),
                }),
        'docnaet_category_id': fields.related(
            'partner_id', 'docnaet_category_id', type='many2one',
            relation='res.partner.docnaet', string='Partner category',
            store={
                'res.partner': (
                    _refresh_partner_category_change, ['docnaet_category_id'], 10),
                'docnaet.document': (
                    _refresh_category_auto_change, ['partner_id'], 10),
                }),
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
            #('suspended', 'Suspended'),
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
