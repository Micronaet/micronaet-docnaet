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
import pdb
import sys
import logging
import openerp
import imaplib
import email
import urllib2
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

    # ------------------------------------------------------------------------------------------------------------------
    # Schedule procedure:
    # ------------------------------------------------------------------------------------------------------------------
    def force_import_email_document(self, cr, uid, ids, context=None):
        """ Force current protocol import used for button or list
        """
        ''' Read all mail activated
        '''
        if context is None:
            context = {}

        # Pool used:
        doc_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        program_pool = self.pool.get('docnaet.protocol.template.program')
        company_pool = self.pool.get('res.company')
        user_pool = self.pool.get('res.users')
        partner_pool = self.pool.get('res.partner')

        protocol_proxy = protocol_pool.browse(cr, uid, ids, context=context)[0]

        # Block setup
        block = doc_pool._block_size  # 1000 files every folder block
        block_mode_on = block > 0  # Manage with block mode folder ON

        # Keep docnaet mode as in protocol setup:
        docnaet_mode = protocol_proxy.docnaet_mode
        context['docnaet_mode'] = docnaet_mode

        # Get store folder depend on docnaet mode:
        store_folder = company_pool.get_docnaet_folder_path(cr, uid, subfolder='store', context=context)
        _logger.info('Start read # %s IMAP server [stored in %s: %s]' % (
            len(ids),
            docnaet_mode,
            store_folder,
            ))

        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        eml_program_id = program_pool.get_program_from_extension(cr, uid, 'eml', context=context)
        if_error = ''
        for address in self.browse(cr, uid, ids, context=context):
            ai_on = address.ai_on
            ai_words = address.ai_words or 50
            ai_url_mask = address.ai_url_mask  # 'http://10.0.0.2:8069/gemini/queue?mode={}&id={}&words={}'

            protocol_id = address.protocol_id.id or False
            server = address.host  # '%s:%s' % (address.host, address.port)

            # ----------------------------------------------------------------------------------------------------------
            # Read all email:
            # ----------------------------------------------------------------------------------------------------------
            try:
                if_error = _('Error find imap server: %s' % server)
                if address.SSL:
                    mail = imaplib.IMAP4_SSL(server)  # TODO SSL
                else:
                    mail = imaplib.IMAP4(server)  # TODO SSL

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

                # ------------------------------------------------------------------------------------------------------
                # Add new document Docnaet:
                # ------------------------------------------------------------------------------------------------------
                # Auto type:
                # Use if set up in address:
                type_id = address.type_id.id or False

                # Auto user:
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

                # Auto partner:
                # Try to search partner from 'to address':
                partner_id = False
                if address.auto_partner:
                    to_address = (record.get('To') or '').split(', ')
                    if to_address:  # Take only the first
                        email_address = \
                            to_address[0].split('<')[-1].split('>')[0]
                        if email_address:
                            # Search user:
                            partner_ids = partner_pool.search(cr, uid, [
                                ('email', '=', email_address),
                                ('docnaet_enable', '=', True), #Docnaet partner
                                ], context=context)
                            if partner_ids:
                                partner_id = partner_ids[0]
                                if len(partner_ids) > 1:
                                    _logger.warning(
                                        '%s partner with address: %s' % (
                                            len(partner_ids),
                                            email_address,
                                            ))

                # ------------------------------------------------------------------------------------------------------
                # Labnaet setup:
                # ------------------------------------------------------------------------------------------------------
                if docnaet_mode == 'labnaet':
                    labnaet_id = doc_pool.get_counter_labnaet_id(cr, uid, context=context)
                else:
                    labnaet_id = False

                data = {
                    'docnaet_mode': docnaet_mode,
                    'labnaet_id': labnaet_id,
                    'protocol_id': protocol_id,
                    'user_id': user_id,
                    'name': record['Subject'] or '...',
                    'partner_id': partner_id,
                    'type_id': type_id,
                    'import_date': now,
                    'uploaded': True,
                    'docnaet_extension': 'eml',
                    'program_id': eml_program_id,
                    # 'language_id':
                    # 'date':
                    }
                if protocol_id and address.auto_number:
                    data['number'] = protocol_pool.assign_protocol_number(
                        cr, uid, data['protocol_id'], context=context)

                # -------------------------------------------------------------
                # Create ID for Docnaet / Labnaet:
                # -------------------------------------------------------------
                doc_id = doc_pool.create(cr, uid, data, context=context)
                if docnaet_mode == 'labnaet':
                    doc_id = labnaet_id

                _logger.info('Read mail: To: %s - From: %s - Subject: %s' % (
                    record['To'],
                    record['From'],
                    record['Subject'],
                    ))

                # -------------------------------------------------------------
                # Write on file:
                # -------------------------------------------------------------
                block_folder = store_folder  # Save temporary in store

                # A. Block folder mode (new):
                if block_mode_on:
                    try:
                        block_folder = os.path.join(store_folder, str(doc_id / block))
                        os.system('mkdir -p %s' % block_folder)
                    except:
                        _logger.error('Error checking document block folder! Saved in store for now')

                # store_folder file:
                eml_file = '%s.eml' % (os.path.join(block_folder, str(doc_id)))
                f_eml = open(eml_file, 'w')
                f_eml.write(eml_string)
                # todo remove file after confirm
                f_eml.close()

                # Mark as deleted:
                mail.store(msg_id, '+FLAGS', '\\Deleted')

                # ------------------------------------------------------------------------------------------------------
                # Gemini AI: Call ODOO for Gemini auto content for description
                # ------------------------------------------------------------------------------------------------------
                if ai_on:
                    # todo pass email file: eml_file?
                    url = ai_url_mask.format(docnaet_mode, doc_id, ai_words)
                    try:
                        _logger.info('Calling ODOO AI url: {}...'.format(url))
                        response = urllib2.urlopen(url)
                        # html = response.read()
                        # _logger.info(response.info())
                        response.close()
                    except urllib2.URLError as e:
                        _logger.error('Error opening URL: {}\n{}'.format(url, e))
                    except urllib2.HTTPError as e:
                        _logger.error('HTTP Error: {}\n{}'.format(e.code, e.msg))
                    except Exception as e:
                        _logger.error('An unexpected error occurred: {}'.format(e))

            _logger.info('End read IMAP %s [tot msg: %s]' % (address.name, tot))

        # -----------------------------------------------------------------
        # Close operations:
        # -----------------------------------------------------------------
        # mail.expunge() # TODO clean trash bin
        mail.close()
        mail.logout()
        _logger.info('End read IMAP server')
        return True

    def schedule_import_email_document(self, cr, uid, context=None):
        """ Search schedule address and launch importation:
        """
        address_ids = self.search(cr, uid, [
             ('is_active', '=', True),
             ], context=context)

        return self.force_import_email_document(
            cr, uid, address_ids, context=context)

    _columns = {
        'ai_on': fields.boolean('AI', help='Attiva la descrizione automatica leggendo la mail'),
        'ai_words': fields.integer('AI parole max',  help='Massimo numero di parole da usare nel riassunto'),
        'ai_words': fields.char(
            'AI ODOO URL', size=180, help='Indirizzo usato per la chiamata asincrona di ODOO'),

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
        'type_id': fields.many2one(
            'docnaet.type', 'Type',
            help='Assign auto type of docnaet document'),
        'docnaet_mode': fields.related(
            'protocol_id', 'docnaet_mode',
            type='selection', string='Docnaet mode',
            selection=[('docnaet', 'Docnaet'),('labnaet', 'Labnaet'),],
            )
        }

    _defaults = {
       'ai_words': lambda *w: 50,
       'ai_url_mask': lambda *u: 'http://10.0.0.2:8069/gemini/queue?mode={}&id={}&words={}',

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

