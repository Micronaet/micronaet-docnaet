# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import imaplib
import email
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

class DocnaetProtocolEmail(orm.Model):
    """ Model name: DocnaetProtocolEmail
    """
    _name = 'docnaet.protocol.email'
    _description = 'Protocol email'
    _rec_name = 'name'
    _order = 'name'
    
    # -------------------------------------------------------------------------
    # Schedule procedure:
    # -------------------------------------------------------------------------
    def force_import_email_document(self, cr, uid, ids, context=None):
        ''' Force current protocol import used for button or list
        '''
        ''' Read all mail activated
        '''        
        # Pool used:
        doc_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        program_pool = self.pool.get('docnaet.protocol.template.program')
        company_pool = self.pool.get('res.company')
        user_pool = self.pool.get('res.users')
        partner_pool = self.pool.get('res.partner')

        store_folder = company_pool.get_docnaet_folder_path(
            cr, uid, subfolder='store', context=context)
        _logger.info('Start read # %s IMAP server [stored in: %s]' % (
            len(ids), 
            store_folder,
            ))
        
        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        eml_program_id = program_pool.get_program_from_extension(
            cr, uid, 'eml', context=context)
        for address in self.browse(cr, uid, ids, context=context):
            protocol_id = address.protocol_id.id or False
            server = address.host #'%s:%s' % (address.host, address.port)

            # -----------------------------------------------------------------
            # Read all email:
            # -----------------------------------------------------------------
            try:
                if_error = _('Error find imap server: %s' % server)
                if address.SSL:
                    mail = imaplib.IMAP4_SSL(server) # TODO SSL
                else:
                    mail = imaplib.IMAP4(server) # TODO SSL
                
                if_error = _('Error login access user: %s' % address.user)
                mail.login(address.user, address.password)
                
                if_error = _('Error access start folder: %s' % address.folder)
                mail.select(address.folder)
            except:
                raise osv.except_osv(
                    _('IMAP server error:'), 
                    if_error,
                    )        
                    
            esit, result = mail.search(None, 'ALL')
            tot = 0
            for msg_id in result[0].split():
                tot += 1
                # Read and parse result:
                esit, result = mail.fetch(msg_id, '(RFC822)')
                eml_string = result[0][1]
                message = email.message_from_string(eml_string)
                record = {
                    'To': False,
                    'From': False,
                    'Date': False,
                    'Received': False,
                    'Message-ID': False,
                    'Subject': False,        
                    }
                    
                # Populate parameters:
                for (param, value) in message.items():
                    if param in record:
                        record[param] = value
                
                # -------------------------------------------------------------
                # Add new document Docnaet:
                # -------------------------------------------------------------
                # Try to search user from 'from address':
                email_address = (
                    record.get('From') or '').split('<')[-1].split('>')[0]
                user_id = 1
                if email_address:
                    # Search user:
                    user_ids = user_pool.search(cr, uid, [
                        ('email', '=', email_address),
                        ], context=context)
                    if user_ids:
                        user_id = user_ids[0]
                        
                # Try to search partner from 'to address':
                partner_id = False
                if address.auto_partner:
                    to_address = (record.get('To') or '').split(', ')
                    if to_address: # Take only the first                   
                        email_address = \
                            to_address[0].split('<')[-1].split('>')[0]
                        if email_address:
                            # Search user:
                            partner_ids = partner_pool.search(cr, uid, [
                                ('email', '=', email_address),
                                ], context=context)
                            if partner_ids:
                                partner_id = partner_ids[0]
                                if len(partner_ids) > 1:
                                    _logger.warning(
                                        '%s partner with address: %s' % (
                                            len(partner_ids),
                                            email_address,
                                            ))

                data = {
                    'protocol_id': protocol_id,
                    'user_id': user_id,
                    'name': record['Subject'] or '...',
                    'partner_id': partner_id,
                    #'language_id': 
                    #'type_id': 
                    #'date': 
                    'import_date': now,
                    'uploaded': True,
                    'docnaet_extension': 'eml',
                    'program_id': eml_program_id,
                    }
                if protocol_id and address.auto_number:
                    data['number'] = protocol_pool.assign_protocol_number(
                        cr, uid, data['protocol_id'], context=context)                
                    
                doc_id = doc_pool.create(cr, uid, data, context=context)
                _logger.info('Read mail: To: %s - From: %s - Subject: %s' % (
                    record['To'],
                    record['From'],
                    record['Subject'],
                    ))

                # -------------------------------------------------------------
                # Write on file:
                # -------------------------------------------------------------
                eml_file = '%s.eml' % (os.path.join(
                    store_folder, 
                    str(doc_id),
                    ))                
                f_eml = open(eml_file, 'w')
                f_eml.write(eml_string)
                # TODO remove file after confirm
                f_eml.close()

                # Mark as deleted:    
                mail.store(msg_id, '+FLAGS', '\\Deleted')    
            _logger.info('End read IMAP %s [tot msg: %s]' % (
                address.name,
                tot,
                ))

        # -----------------------------------------------------------------
        # Close operations:    
        # -----------------------------------------------------------------
        #mail.expunge() # TODO clean trash bin
        mail.close()
        mail.logout()
        _logger.info('End read IMAP server')
        return True
    
    def schedule_import_email_document(self, cr, uid, context=None):
        ''' Search schedule address and launch importation:
        '''
        address_ids = self.search(cr, uid, [
             ('is_active', '=', True),
             ], context=context)
        
        return self.force_import_email_document(
            cr, uid, address_ids, context=context)
    
    _columns = {  
        'is_active': fields.boolean('Is active'),
        'name': fields.char('Email', size=64, required=True),
        'host': fields.char(
            'IMAP server', size=64, help='Email IMAP server', required=True),
        'port': fields.integer('Port', required=True),
        'user': fields.char(
            'Username', size=64, help='Email user', required=True),
        'password': fields.char(
            'Password', size=64, help='Email password', required=True),
        'folder': fields.char(
            'Folder', size=64, help='Email IMAP folder'),
        'SSL': fields.boolean('SSL'),
        'auto_number': fields.boolean('Auto protocol number', 
            help='Assign next number of protocol after import'),
        'auto_partner': fields.boolean('Auto partner',
            help='Try to assign partner from email address'),        
        'remove': fields.boolean('Remove after import'),
        'protocol_id': fields.many2one(
            'docnaet.protocol', 'Protocol', required=True),
        }
    
    _defaults = {
       'port': lambda *a: 993,
       'SSL': lambda *a: True,
       'folder': lambda *a: 'INBOX',
       }

class DocnaetProtocol(orm.Model):
    """ Model name: DocnaetProtocol
    """
    _inherit = 'docnaet.protocol'
    
    _columns = {
        'auto_email': fields.boolean('Auto email'),
        'account_ids': fields.one2many(
            'docnaet.protocol.email', 'protocol_id', 'Account'),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:1111111
