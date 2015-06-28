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

# TODO res.country
class ResCompany(orm.Model):
    ''' Docnaet company extra fields
    '''
    _inherit = 'res.company'
    _columns = {
        'docnaet_path': fields.char(
            'Docnaet path', size=64, 
            help='Docnaet root path in file system for store docs'), 
        }

class DocnaetProtocolTemplateProgram(orm.Model):
    ''' Object docnaet.protocol.template.program
    '''    
    
    _name = 'docnaet.protocol.template.program'
    _description = 'Docnaet program'
                    
    _columns = {        
        'name': fields.char('Language', size=64, required=True),
        'extension': fields.char('Extension', size=5),
        'note': fields.text('Note'),
        }

class DocnaetLanguage(orm.Model):
    ''' Object docnaet.language
    '''    
    
    _name = 'docnaet.language'
    _description = 'Docnaet language'
                    
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
    

    _columns = {        
        'name': fields.char('Type', size=64, required=True),
        'note': fields.text('Note'),
        }

class DocnaetProtocol(orm.Model):
    ''' Object docnaet.protocol
    '''    
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'

    _columns = {        
        'name': fields.char('Protocol', size=64, required=True),
        'next': fields.integer('Next protocol', required=True), 
        'note': fields.text('Note'),
        }

class DocnaetProtocolTemplate(orm.Model):
    ''' Object docnaet.protocol.template
    '''    
    _name = 'docnaet.protocol.template'
    _description = 'Docnaet protocol template'
    _rec_name = 'lang_id'

    _columns = {
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol'),
        'lang_id': fields.many2one('docnaet.language', 'Language', 
            required=True),
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
    _order = 'date,name'

        
    # -------------------------------------------------
    # Utility for URL creation:
    # -------------------------------------------------
    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        return self.call_url(cr, uid, ids[0], context=context)

    def button_call_url_document(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        return self.call_url(
            cr, uid, ids[0], docnaet_format=True, context=context)
        
    # TODO modify for open in OpenERP not docnaet    
    def call_url(self, cr, uid, item_id, docnaet_format=False,  context=None):
        ''' Call url if format: docnaet://
            item_id: ID of docnaet.document
            docnaet_format: 
                True= in docnaet format require installation of 
                docnaet.exe element + registry entry for launch
                docnaet:// special link
                
                False= Get the link for open detail of document 
                directly in Docnaet passing autentication form
        '''        
        docnaet_proxy = self.browse(cr, uid, item_id, context=context)

        if docnaet_format: # docnaet://
            final_url = r"docnaet://%s\%s\%s.%s"%(
                docnaet_proxy.docnaet_company_id, 
                docnaet_proxy.docnaet_protocol_id,
                docnaet_proxy.docnaet_document_real_id if \
                    docnaet_proxy.docnaet_document_real_id else \
                    docnaet_proxy.docnaet_document_id,
                docnaet_proxy.docnaet_extension,     
                )
        else: # Link to detail form in docnaet
            parameters = self.pool.get('res.company').get_docnaet_parameters(
                cr, uid, context=context)
            final_url = r"http://%s/docnaet/asp/autenticazione.asp?token=T&client_id=%s&document_id=%s&company_id=%s&user_id=%s" % (
                parameters.docnaet_host, 
                docnaet_proxy.docnaet_client_id, 
                docnaet_proxy.docnaet_document_id, 
                docnaet_proxy.docnaet_company_id, 
                docnaet_proxy.docnaet_user_id \
                    if docnaet_proxy.docnaet_user_id \
                    else parameters.docnaet_guest_user_id.id,
                )

        return {'type': 'ir.actions.act_url', 'url':final_url, 'target': 'new'}
                        
    _columns = {        
        'name': fields.char('Oggetto', size=64),
        'number': fields.char('Prot. n.', size=10),
        'date': fields.date('Date'),
        'deadline': fields.date('Deadline'),
        'deadline_extra': fields.char('Deadline info', size=64),
        'description': fields.text('Description'),
        'note': fields.text('Note'),

        # OpenERP ID-many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol'),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'type_id': fields.many2one('docnaet.type', 'Type'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'User'),
        'partner_id': fields.many2one('res.partner', 'Partner'),

        'docnaet_extension': fields.char('Docnaet files ext.', size = 5),       

        # TODO remove for directly open in OpenERP
        # Docnaet ID (for open document)
        #'docnaet_document_id': fields.integer('Docnaet Document ID'),
        #'docnaet_document_real_id': fields.integer('Docnaet Document RealID'),
        #'docnaet_protocol_id': fields.integer('Docnaet Protocol ID'),
        #'docnaet_language_id': fields.integer('Docnaet Language ID'),
        #'docnaet_type_id': fields.integer('Docnaet Type ID'),
        #'docnaet_company_id': fields.integer('Docnaet Company ID'),  

        #'docnaet_client_id': fields.integer('Docnaet Client ID'),
        #'docnaet_user_id': fields.integer('Docnaet User ID'),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
