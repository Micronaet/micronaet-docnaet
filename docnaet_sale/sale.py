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
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    DATETIME_FORMATS_MAP,
    float_compare)


_logger = logging.getLogger(__name__)


class CRMLostDetail(orm.Model):
    """ Model name: CRM Lost Detail
    """

    _name = 'crm.lost.detail'
    _description = 'Dettaglio offerta persa'
    _rec_name = 'name'
    _order = 'name'

    _columns = {
        'name': fields.char(
            'Name', size=64, required=True,
            ),
        'note': fields.text('Note'),
    }


class DocnaetProtocol(orm.Model):
    """ Add extra fields for integrare a link to docnaet document
    """
    _inherit = 'docnaet.protocol'

    _columns = {
        'sale_management': fields.boolean('CRM management'),
        }


class ResCompany(orm.Model):
    """ Add extra fields for docnaet parameter
    """
    _inherit = 'res.company'

    _columns = {
        'docnaet_mask_link': fields.char(
            'Maschera link', size=120,
            help='Maschera da utilizzare per inviara i link dei documenti'
                 'tramite email, lasciare la %s per indicare la posizione'
                 'dell\'ID documento'),
        }


class DocnaetDocument(orm.Model):
    """ Add extra fields for integrare a link to docnaet document
    """
    _inherit = 'docnaet.document'

    def show_linked_sale_ids(self, cr, uid, ids, context=None):
        """ Open Sale order document (overridden?)
        """
        current = self.browse(cr, uid, ids, context=context)[0]
        order_ids = [o.id for o in current.linked_sale_ids]

        model_pool = self.pool.get('ir.model.data')
        form_view_id = model_pool.get_object_reference(cr, uid, 'sapnaet', 'view_sale_order_matrix_form')[1]
        tree_view_id = model_pool.get_object_reference(
            cr, uid, 'sapnaet', 'sale_order_for_delivery_operation_deadline_view_tree')[1]

        if not order_ids:  # No order
            raise
        elif len(order_ids) == 1:  # Single order
            return {
                'type': 'ir.actions.act_window',
                'name': _('Ordine collegato al documento Docnaet'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': order_ids[0],
                'res_model': 'sale.order',
                'view_id': form_view_id,
                'views': [(form_view_id, 'form')],
                'domain': [],
                'context': context,
                'target': 'current',
                'nodestroy': False,
            }
        else:  # Many orders
            return {
                'type': 'ir.actions.act_window',
                'name': _('Ordini collegati al documento Docnaet'),
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_id': False,
                'res_model': 'sale.order',
                'view_id': tree_view_id,
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'domain': [('id', 'in', order_ids)],
                'context': context,
                'target': 'current',
                'nodestroy': False,
            }

    def scheduled_raise_pending_offer(self, cr, uid, context=None):
        """ Mail when offer passed limit
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company = user.company_id
        docnaet_mask_link = company.docnaet_mask_link

        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)[:10]
        document_ids = self.search(cr, uid, [
            ('sale_state', '=', 'pending'),
            ('sale_order_amount', '>', 0),
            ('deadline', '<=', now),
        ], context=context)
        user_mail = {}
        for document in self.browse(cr, uid, document_ids, context=context):
            user = document.user_id
            if user not in user_mail:
                user_mail[user] = []
            user_mail[user].append(document)

        mailer = self.pool.get('ir.mail_server')

        if not user_mail:
            _logger.warning('No message for CRM deadline!')
            return False

        # ---------------------------------------------------------------------
        #                         SMTP connection:
        # ---------------------------------------------------------------------
        # Get mail server option from OpenERP:
        mailer_ids = mailer.search(cr, uid, [], context=context)
        if not mailer_ids:
            _logger.error('No mail server configured in ODOO')
            return False
        mailer = mailer.browse(cr, uid, mailer_ids, context=context)[0]

        # Open connection:
        _logger.info('[INFO] Sending using "%s" connection [%s:%s]' % (
            mailer.name, mailer.smtp_host, mailer.smtp_port))

        if mailer.smtp_encryption in ('ssl', 'starttls'):
            smtp_server = smtplib.SMTP_SSL(
                mailer.smtp_host, mailer.smtp_port)
        else:
            _logger.error('Connect only SMTP SSL server!')
            return False

        smtp_server.login(mailer.smtp_user, mailer.smtp_pass)
        for user in user_mail:
            to = user.email
            if not to:
                _logger.error('Cannot send mail, no address on user!')
                continue

            css = '''
                p {
                    margin: 25px 0;
                    font-size: 0.9em;
                    font-family: sans-serif;
                }
                .styled-table {
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    font-family: sans-serif;
                    min-width: 500px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }
                .styled-table thead tr {
                    background-color: #009879;
                    color: #ffffff;
                    text-align: left;
                }
                .styled-table th,
                .styled-table td {
                    padding: 12px 15px;
                }
                .styled-table tbody tr {
                    border-bottom: 1px solid #dddddd;
                }
                
                .styled-table tbody tr:nth-of-type(even) {
                    background-color: #f3f3f3;
                }
                
                .styled-table tbody tr:last-of-type {
                    border-bottom: 2px solid #009879;
                }
                .styled-table tbody tr.active-row {
                    font-weight: bold;
                    color: #009879;
                }            
            '''
            html_body = '<html>' \
                        '<head><title>CRM OpenERP</title>' \
                        '<style>%s</style>' \
                        '</head>' \
                        '<body>' \
                        '<p>Spett.le %s<br/>in allegato il dettaglio delle ' \
                        'offerte scadute oggi, il link permette di aprirle ' \
                        'in OpenERP.<br/>Mail automatica di OpenERP' \
                        '</p>' % (css, user.name)
            html_body += '<p><table class="styled-table">' \
                         '<tr><th>Comando</td><th>Data</th><th>Cliente</th>' \
                         '<th>Dettaglio</th><th>Oggetto</th>' \
                         '<th>Scadenza</th></tr>'

            for document in user_mail[user]:
                document_id = document.id
                html_body += \
                    '<tr><td><a href="%s">APRI</a>' \
                    '</td><td>%s</td><td>%s</td><td>%s: %s</td>' \
                    '<td>%s</td><td>%s</td></tr>' % (
                        docnaet_mask_link % document_id,
                        document.date or '',
                        document.partner_id.name,
                        document.protocol_id.name,
                        document.number,
                        document.name or '',
                        document.deadline or '',
                        )
            html_body += '</table></body></html>'
            print('Sending mail to: %s ...' % to)
            msg = MIMEMultipart()
            msg['Subject'] = 'CRM OpenERP: Dettaglio offerte scadute'
            msg['From'] = mailer.smtp_user
            msg['To'] = to
            msg.attach(MIMEText(html_body, 'html'))

            # Send mail:
            smtp_server.sendmail(mailer.smtp_user, to, msg.as_string())
        smtp_server.quit()
        return True

    def onchange_no_sale_price(
            self, cr, uid, ids, no_sale_price, context=None):
        """ Clean price if removed check
        """
        res = {}
        if not no_sale_price:
            return res
        res['value'] = {
            'sale_order_amount': 0.0,
            }
        return res

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def check_amount_present(self, cr, uid, ids, context=None):
        """ Check if manatory amount
        """
        assert len(ids) == 1, 'Works only with one record a time'

        document = self.browse(cr, uid, ids, context=context)[0]
        if document.protocol_id.sale_management and \
                not document.no_sale_price and not document.sale_order_amount:
            raise osv.except_osv(
                _('Errore'),
                _('''Il documento richiede, nella sezione CRM, una indicazione
                 di importo offerta obbligatoria (a meno di escluderla 
                 impostando: 'nessuna valorizzazione')!'''),
                )

    # -------------------------------------------------------------------------
    # OVERRIDE: Workflow docnaet event:
    # -------------------------------------------------------------------------
    def document_confirmed(self, cr, uid, ids, context=None):
        """ Check before confirmed
        """
        self.check_amount_present(cr, uid, ids, context=context)
        return super(DocnaetDocument, self).document_confirmed(
            cr, uid, ids, context=context)

    def document_timed(self, cr, uid, ids, context=None):
        """ Check before timed
        """
        self.check_amount_present(cr, uid, ids, context=context)
        return super(DocnaetDocument, self).document_timed(
            cr, uid, ids, context=context)

    # -------------------------------------------------------------------------
    # Workflow sale event:
    # -------------------------------------------------------------------------
    def sale_order_pending(self, cr, uid, ids, context=None):
        """ Workflow set pending
        """
        return self.write(cr, uid, ids, {
            'sale_state': 'pending',
            }, context=context)

    def sale_order_win(self, cr, uid, ids, context=None):
        """ Workflow set win
        """
        return self.write(cr, uid, ids, {
            'sale_state': 'win',
            }, context=context)

    def sale_order_lost(self, cr, uid, ids, context=None):
        """ Workflow set lost
        """
        return self.write(cr, uid, ids, {
            'sale_state': 'lost',
            }, context=context)

    def sale_order_remake(self, cr, uid, ids, context=None):
        """ Workflow set remake
        """
        return self.write(cr, uid, ids, {
            'sale_state': 'remake',
            }, context=context)

    def sale_order_pending_offer(self, cr, uid, ids, context=None):
        """ Return view of pending offer
        """
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        partner_id = current_proxy.partner_id.id
        document_ids = self.search(cr, uid, [
            ('id', '!=', ids[0]),
            ('partner_id', '=', partner_id),
            ('sale_state', '=', 'pending'),
            ], context=context)
        if document_ids:
            view_id = False
            return {
                'type': 'ir.actions.act_window',
                'name': _('Pending offer'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'res_id': 1,
                'res_model': 'docnaet.document',
                'view_id': view_id,  # False
                'views': [(False, 'tree'), (False, 'form')],
                'domain': [('id', 'in', document_ids)],
                'context': context,
                'target': 'current',  # 'new'
                'nodestroy': False,
                }
        else:
            raise osv.except_osv(
                _('Info:'),
                _('No pending offer!'),
                )

    _columns = {
        # Link to sale.order
        'link_sale': fields.boolean(
            'Link',
            help='Link document in sale form'),
        'linked_sale_ids': fields.many2many(
            'sale.order', 'docnaet_linked_sale_rel',
            'docnaet_id', 'sale_id',
            'Offerte/Ordini collegati'),
        # todo remove:
        'linked_sale_id': fields.many2one(
            'sale.order', 'Linked sale'),

        # CRM management:
        'sale_management': fields.related(
            'protocol_id', 'sale_management',
            type='boolean', string='Gestione CRM'),
        'no_sale_price': fields.boolean(
            'Nessuna valorizzazione',
            help='Non va indicata la valorizzazione perché non esiste'),
        'sale_comment': fields.text('Sale comment',
            help='Why we lost or win the quotation'),
        'sale_order_amount': fields.float('Total sale', digits=(16, 2)),
        'sale_currency_id': fields.many2one('res.currency', 'Currency'),
        'sale_state': fields.selection([
            ('pending', 'Pending'),
            ('win', 'Win'),
            ('lost', 'Lost'),
            ('remake', 'Rinegoziata'),
            ], 'Sale state'),
        'sale_lost_cause_ids': fields.many2many(
            'crm.lost.detail', 'crm_sale_state_lost_rel',
            'document_id', 'lost_id',
            'Motivi perdita'),
        }

    _defaults = {
        'sale_state': lambda *x: 'pending',
        'link_sale': lambda *x: True,
        'sale_currency_id': lambda *x: 1,  # TODO better
        }


class SaleOrder(orm.Model):
    """ Add extra fields for integrate docnaet document
    """
    _inherit = 'sale.order'

    _columns = {
        'docnaet_ids': fields.many2many(
            'docnaet.document', 'docnaet_linked_sale_rel',
            'sale_id', 'docnaet_id',
            'Documenti Docnaet'),

        # 'docnaet_ids': fields.one2many(
        #    'docnaet.document', 'linked_sale_id',
        #    'Docnaet document'),
        }
