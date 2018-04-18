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
            context: used field_path for read correct path name in company    
        '''
        if context is None:
            context = {}
        field_path = context.get('field_path', 'docnaet_path')
        
        # Get docnaet path from company element
        company_ids = self.search(cr, uid, [], context=context)
        company_proxy = self.browse(cr, uid, company_ids, context=context)[0]
        docnaet_path = company_proxy.__getattr__(field_path)# XXX variable
        
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
        'labnaet_path': fields.char(
            'Labnaet path', size=64, required=True,
            help='Labnaet root path in file system for store docs'), 
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
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            ('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }

    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
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
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            ('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }
        
    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
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
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            ('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }
        
    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
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
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            ('all', 'All'), # TODO remove?!?
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }
        
    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
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
    # Onchange event:
    # -------------------------------------------------------------------------
    def onchange_country_partner_domain(self, cr, uid, ids, 
            search_partner_name, search_country_id, #category_id, 
            context=None):
        ''' On change for domain purpose
        '''
        res = {}
        res['domain'] = {'partner_id': [
            ('docnaet_enable', '=', True),
            ]}        
        
        if search_country_id:
            res['domain']['partner_id'].append(
                ('country_id', '=', search_country_id),
                )
        if search_partner_name:
            if '+' in search_partner_name:
                partner_part = search_partner_name.split('+')
                # Add or:
                #res['domain']['partner_id'].extend([
                #    '|' for item in range(1, len(partner_part))])
                # Add partner list of ilike search:    
                res['domain']['partner_id'].extend([
                    ('name', 'ilike', p) for p in partner_part])
            else:   
                res['domain']['partner_id'].append(
                    ('name', 'ilike', search_partner_name),
                    )
        #if category_id:
        #    res['domain']['partner_id'].append(
        #        ('docnaet_category_id','=', category_id),
        #        )
        _logger.warning('Filter: %s' % res)
        return res

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
        if context is None:
            context = {}
        context['field_path'] = '%s_path' % document.docnaet_mode
        if document.docnaet_mode == 'labnaet':
            document_id = document.labnaet_id
        else:#elif document.docnaet_mode == 'labnaet': # XXX labnaet mode
            document_id = document.id
            
        
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
            filename = '%s.%s' % (document_id, document.docnaet_extension)
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

    def _get_date_month_4_group(self, cr, uid, ids, fields, args, 
            context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for doc in self.browse(cr, uid, ids, context=context):
            if doc.date:
                res[doc.id] = ('%s' % doc.date)[:7]
            else:
                res[doc.id] = _('Nessuna')
        return res

    def _get_deadline_month_4_group(self, cr, uid, ids, fields, args, 
            context=None):
        ''' Fields function for calculate 
        '''
        res = {}
        for doc in self.browse(cr, uid, ids, context=context):
            if doc.deadline:
                res[doc.id] = ('%s' % doc.deadline)[:7]
            else:
                res[doc.id] = _('Nessuna')
        return res
    
    def _store_data_deadline_month(self, cr, uid, ids, context=None):
        ''' if change date reload data
        '''
        _logger.warning('Change date_mont depend on date and deadline')
        return ids
            
    _columns = {        
        'name': fields.char('Subject', size=180, required=True),
        'labnaet_id': fields.integer('Labnaet ID', 
            help='Secondary ID for document, keep data in different folder.'),
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
            type='char', string='Mese inser.', size=15,
            store={
                'docnaet.document': (
                    _store_data_deadline_month, ['date'], 10),
                }), 
                        
        'deadline_info': fields.char('Deadline info', size=64),
        'deadline': fields.date('Deadline'),
        'deadline_month': fields.function(
            _get_deadline_month_4_group, method=True, 
            type='char', string='Scadenza', size=15, 
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
                    _refresh_partner_category_change, [
                        'docnaet_category_id'], 10),
                'docnaet.document': (
                    _refresh_category_auto_change, ['partner_id'], 10),
                }),
        # Search partner extra fields:
        'search_partner_name': fields.char(
            'Search per Partner name', size=80),
        'search_country_id': fields.many2one(
            'res.country', 'Search per Country'),
                
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
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            #('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),

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
        'docnaet_mode': lambda *x: 'docnaet',
        'date': lambda *x: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
        'priority': lambda *x: 'normal',
        'state': lambda *x: 'draft',        
        }    

class DocnaetDocument(orm.Model):
    ''' Add extra relation fields
    '''          
    _inherit = 'docnaet.document'

    _columns = {
        'duplicated_ids': fields.one2many('docnaet.document', 'original_id',
            'duplicated', help='Child document duplicated from this'),
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
