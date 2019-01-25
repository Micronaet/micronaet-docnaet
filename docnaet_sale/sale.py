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

class DocnaetProtocol(orm.Model):
    ''' Add extra fields for integrare a link to docnaet document
    '''
    _inherit = 'docnaet.protocol'
    
    _columns = {
        'sale_management': fields.boolean('CRM management'),
        }

class DocnaetDocument(orm.Model):
    ''' Add extra fields for integrare a link to docnaet document
    '''
    _inherit = 'docnaet.document'
    
    # -------------------------------------------------------------------------
    # Workflow sale event:
    # -------------------------------------------------------------------------
    def sale_order_pending(self, cr, uid, ids, context=None):
        ''' Workflow set pending
        '''
        return self.write(cr, uid, ids, {
            'sale_state': 'pending',
            }, context=context)
    def sale_order_win(self, cr, uid, ids, context=None):
        ''' Workflow set win
        '''
        return self.write(cr, uid, ids, {
            'sale_state': 'win',
            }, context=context)
    def sale_order_lost(self, cr, uid, ids, context=None):
        ''' Workflow set lost
        '''
        return self.write(cr, uid, ids, {
            'sale_state': 'lost',
            }, context=context)
    
    def sale_order_pending_offer(self, cr, uid, ids, context=None):
        ''' Return view of pending offer
        '''
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
                #'res_id': 1,
                'res_model': 'docnaet.document',
                'view_id': view_id, # False
                'views': [(False, 'tree'), (False, 'form')],
                'domain': [('id', 'in', document_ids)],
                'context': context,
                'target': 'current', # 'new'
                'nodestroy': False,
                }
        else:
            raise osv.except_osv(
                _('Info:'), 
                _('No pending offer!'),
                )

    _columns = {
        'linked_sale_id': fields.many2one(
            'sale.order', 'Linked sale'),
        'link_sale': fields.boolean('Link', 
            help='Link document in sale form'),

        # CRM management:
        'sale_order_amount': fields.float('Total sale', digits=(16, 2)),
        'sale_currency_id': fields.many2one('res.currency', 'Currency'),
        'sale_state': fields.selection([
            ('pending', 'Pending'),
            ('win', 'Win'),
            ('lost', 'Lost'),
            ], 'Sale state'),
        }

    _defaults = {
        'sale_state': lambda *x: 'pending',
        'link_sale': lambda *x: True,
        'sale_currency_id': lambda *x: 1, # TODO better
        }

class SaleOrder(orm.Model):
    ''' Add extra fields for integrare docnaet document
    '''
    _inherit = 'sale.order'
    
    _columns = {
        'docnaet_ids': fields.one2many('docnaet.document', 'linked_sale_id',
            'Docnaet document'),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
