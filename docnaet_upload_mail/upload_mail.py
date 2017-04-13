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
    def schedule_import_email_document(self, cr, iud, ids, context=None):
        ''' Read all mail activated
        '''
        # Pool used:
        doc_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        company_pool = self.pool.get('res.company')

        address_ids = self.search(cr, uid, [], context=context)

        store_folder = company_pool.get_docnaet_folder_path(
            cr, uid, subfolder='store', context=context)
        for address in self.browse(cr, iud, address_ids, context=context):
            server = '%s:%s' % (address.host, address.port)
            ssl = address.SSL
            
            # -----------------------------------------------------------------
            # Read all email:
            # -----------------------------------------------------------------
            mail = imaplib.IMAP4_SSL(server) # TODO SSL
            mail.login(address.user, address.password)
            mail.select(address.folder)
            esit, data = mail.search(None, 'ALL')
            for msg_id in data[0].split():
                # Read and parse data:
                esit, data = mail.fetch(msg_id, '(RFC822)')
                eml_string = data[0][1]
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
                # Add new documento Docnaet:
                # -------------------------------------------------------------
                email = (record.get('From') or '').split('<')[-1].split('>')[0]
                if email:
                    # Search user:
                    user_id = user_pool.search(cr, uid, [
                        ('email', '=', email)], context=context)
                else:
                    user_id = 1 # better not go there!
                protocol_id = address.protocol_id.id or False
                doc_id = doc_pool.create(cr, uid, {
                    'protocol_id': protocol_id,
                    'user_id': user_id,
                    'name': record['Subject'] or '...',
                    #'partner_id': wiz_proxy.default_partner_id.id or False, 
                    #'language_id': wiz_proxy.default_language_id.id or False, 
                    #'type_id': wiz_proxy.default_type_id.id or False,
                    #'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'import_date': datetime.now().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                    'uploaded': True,
                    'docnaet_extension': 'eml',
                    'program_id': program_pool.get_program_from_extension(
                        cr, uid, 'eml', context=context)
                    }, context=context)
                if protocol_id and address.auto_number:
                    data['number'] = protocol_pool.assign_protocol_number(
                        cr, uid, data['protocol_id'], context=context)                
                
                _logger.info('Read mail: To: %s - From: %s - Subject: %s' % (
                    record['To'],
                    record['From'],
                    record['Subject'],
                    ))
                # Mark as deleted:    
                mail.store(msg_id, '+FLAGS', '\\Deleted')    

                # -------------------------------------------------------------
                # Write on file:
                # -------------------------------------------------------------
                eml_file = '%s.eml' % (os.path.join(
                    store_folder, 
                    doc_id,
                    ))                
                f_eml = open(eml_file, 'w')
                f_eml.write(eml_string)
                # TODO remove file after confirm
                f_eml.close()

        # -----------------------------------------------------------------
        # Close operations:    
        # -----------------------------------------------------------------
        #mail.expunge() # TODO clean trash bin
        mail.close()
        mail.logout()
    
    _columns = {  
        'is_active': fields.boolean('Is active'),
        'name': fields.char('Email', size=64, required=True),
        'host': fields.char(
            'host', size=64, help='Email IMAP server'),
        'port': fields.integer('Port'),
        'user': fields.char(
            'host', size=64, help='Email user'),
        'password': fields.char(
            'host', size=64, help='Email password'),
        'folder': fields.char(
            'host', size=64, help='Email IMAP folder'),
        'SSL': fields.boolean('SSL'),
        'auto_number': fields.boolean('Auto protocol number'),
        'remove': fields.boolean('Remove after import'),
        'protocol_id': fields.many2one(
            'docnaet.protocol', 'Protocol'),
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
