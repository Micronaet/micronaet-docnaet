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
    _columns = {
        'docnaet_path': fields.char(
            'Docnaet path', size=64, 
            help='Docnaet root path in file system for store docs'), 
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

    _columns = {        
        'name': fields.char('Protocol', size=64, required=True),
        'next': fields.integer('Next protocol', required=True), 
        'note': fields.text('Note'),
        # TODO company_id
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
                    
    _columns = {        
        'name': fields.char('Language', size=64, required=True),
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
        self.write(cr, uid, ids, {
            'state': 'draft',
            }, context=context)
        return True

    def document_confirmed(self, cr, uid, ids, context=None):
        ''' WF confirmed state
        '''
        self.write(cr, uid, ids, {
            'state': 'confirmed',
            }, context=context)
        return True

    def document_suspended(self, cr, uid, ids, context=None):
        ''' WF suspended state
        '''
        self.write(cr, uid, ids, {
            'state': 'suspended',
            }, context=context)
        return True

    def document_timed(self, cr, uid, ids, context=None):
        ''' WF timed state
        '''
        self.write(cr, uid, ids, {
            'state': 'timed',
            }, context=context)
        return True

    def document_cancel(self, cr, uid, ids, context=None):
        ''' WF cancel state
        '''
        self.write(cr, uid, ids, {
            'state': 'cancel',
            }, context=context)
        return True
        
    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def call_docnaet_url(self, cr, uid, ids, mode, context=None):    
        ''' Call url in format: docnaet://[operation] cases:
            [open] protocol - id.ext > open document
            [home] folder > open personal folder (for updload)
            
            NOTE: maybe expand the services
        '''        
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]

        if mode == 'open':  # TODO rimettere id e togliere docnae_id
            final_url = r"docnaet://[open]%s-%s.%s"%(
                doc_proxy.protocol_id.docnaet_id,
                doc_proxy.docnaet_id \
                    if not doc_proxy.original_id \
                    else doc_proxy.original_id.id,
                doc_proxy.docnaet_extension or 'doc', # default doc
                )
        elif mode == 'home':
            final_url = r"docnaet://[home]%s" % 'home_folder' #TODO

        return {'type': 'ir.actions.act_url', 'url':final_url, 'target': 'new'}

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def button_assign_fax_number(self, cr, uid, ids, context=None):
        ''' Assign fax number to document (next counter)
        '''
        return True

    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call url function for prepare address and return for open doc:
        '''
        return self.call_docnaet_url(cr, uid, ids, 'open', context=context)
                       
    _columns = {        
        'name': fields.char('Subject', size=80, required=True),
        'filename': fields.char('File name', size=100),
        'description': fields.text('Description'),
        'note': fields.text('Note'),
        
        'number': fields.char('N.', size=10),
        'fax_number': fields.char('Fax n.', size=10),

        'date': fields.date('Date', required=True),
        'deadline': fields.date('Deadline'),
        'deadline_info': fields.char('Deadline info', size=64),

        # OpenERP many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol', 
            required=True),
        'language_id': fields.many2one('docnaet.language', 'Language'),
        'type_id': fields.many2one('docnaet.type', 'Type'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'docnaet_extension': fields.char('Ext.', size=5),

        'original_id': fields.many2one('docnaet.document', 'Original',
            help='Parent orignal document after this duplication'),

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
