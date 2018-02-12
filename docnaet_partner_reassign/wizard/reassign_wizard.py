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
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class DocnaetPartnerReassignWizard(orm.TransientModel):
    ''' Wizard for reassign partner
    '''
    _name = 'docnaet.partner.reassign.wizard'

    # -------------------------------------------------------------------------
    # On change:
    # -------------------------------------------------------------------------
    def onchange_partner_element(self, cr, uid, ids, from_id, to_id, 
            mode, context=None):
        ''' Update a status field for get informations
        '''
        # Pool used:
        partner_pool = self.pool.get('res.partner')
        document_pool = self.pool.get('docnaet.document')
        
        res = {
            'domain': {
                'to_partner_id': [('sql_customer_code', '!=', False)],
                },
            'value': {
                'status': '',
                },
            }
        
        if mode == 'supplier':
            res['domain']['to_partner_id'] = [
                ('sql_supplier_code', '!=', False)]
                
        if not from_id or not to_id:
            return res

        from_proxy = partner_pool.browse(cr, uid, from_id, context=context)
        to_proxy = partner_pool.browse(cr, uid, to_id, context=context)
        doc_ids = document_pool.search(cr, uid, [
            ('partner_id', '=', from_id),
            ], context=context)

        if not doc_ids:            
            operation = 'Nessuna (no documenti)'
        else:
            operation = 'Migrazione dei documenti al nuovo partner\n'    
            if from_proxy.sql_customer_code or from_proxy.sql_supplier_code or\
                    from_proxy.sql_destination_code: 
                operation += '- Cliente origine disattivato (da gest.)\n'
            else:    
                operation += '- Cliente origine cancellato (da docnaet)\n'
                
            
        res['value']['status'] = u'''
            <table width='100%%'>
                <tr>
                    <th>Campo</th><th>Da</th><th>A</th>
                </tr>
                <tr>
                    <th>Nome</th><td>%s</td><td>%s</td>
                </tr>
                <tr>
                    <th>Docnaet</th><td>%s</td><td>%s</td>
                </tr>
                <tr>
                    <th>Nazione</th><td>%s</td><td>%s</td>
                </tr>
                <tr>
                    <th>Categoria</th><td>%s</td><td>%s</td>
                </tr>                
                <tr>
                    <th>Cod. Cliente</th><td>%s</td><td>%s</td>
                </tr>                
                <tr>
                    <th>Cod. Fornitore</th><td>%s</td><td>%s</td>
                </tr>                
                <tr>
                    <th>Cod. Destinazione</th><td>%s</td><td>%s</td>
                </tr>                
                <tr>
                    <th># Documenti</th><td>%s</td><td>&nbsp;</td>
                </tr>                
                <tr>
                    <th>Operazione</th><td colspan="2">%s</td>
                </tr>                
            </table>
            ''' % (
                from_proxy.name, 
                to_proxy.name,
                
                'SI' if from_proxy.docnaet_enable else 'NO', 
                'SI' if to_proxy.docnaet_enable else 'NO',
                                
                from_proxy.country_id.name or '/', 
                to_proxy.country_id.name or '/',
                
                from_proxy.docnaet_category_id.name or '/',
                to_proxy.docnaet_category_id.name or '/',
                
                from_proxy.sql_customer_code or '/',  
                to_proxy.sql_customer_code or '/',

                from_proxy.sql_supplier_code or '/',  
                to_proxy.sql_supplier_code or '/',

                from_proxy.sql_destination_code or '/',  
                to_proxy.sql_destination_code or '/',
                
                len(doc_ids),
                
                operation,
                )
        return res 
        
    # -------------------------------------------------------------------------
    # Wizard button event:
    # -------------------------------------------------------------------------
    def action_done(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        
        
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]
        from_partner = wiz_browse.from_partner_id
        to_partner = wiz_browse.to_partner_id
        
        # ---------------------------------------------------------------------
        # Update documents:
        # ---------------------------------------------------------------------
        document_pool = self.pool.get('docnaet.document')        
        doc_ids = document_pool.search(cr, uid, [
            ('partner_id', '=', from_partner.id),
            ], context=context)
            
        if not doc_ids:
            raise osv.except_osv(
                _('Error'), 
                _('No document to reassign!'),
                )   
        document_pool.write(cr, uid, doc_ids, {
            'partner_id': to_partner.id,
            }, context=context)         
            
        # ---------------------------------------------------------------------
        # Manage partner:
        # ---------------------------------------------------------------------
        partner_pool = self.pool.get('res.partner')
        data = {
            'docnaet_enable': False,
            }

        # To (only docnaet enable operation):
        partner_pool.write(cr, uid, to_partner.id, {
            'docnaet_enable': True,
            }, context=context)

        # From (mark as invisible if necessary):
        if not(from_partner.sql_customer_code or \
                from_partner.sql_supplier_code or \
                from_partner.sql_destination_code): 
            data = {
                'docnaet_enable': False,
                'active': False,
                }
            _logger.warning(
                'Partner marked as not active: %s' % from_partner.id)    
        else:
            data = {
                'docnaet_enable': False,
                }
            _logger.warning(
                'Partner marked no docnaet: %s' % from_partner.id)        
        partner_pool.write(cr, uid, from_partner.id, data, context=context)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Modified document'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'docnaet.document',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', doc_ids)],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
            
    _columns = {
        'mode': fields.selection([
            ('customer', 'Account customer'),
            ('supplier', 'Account supplier'),            
            ], 'Mode', required=True),
        'from_partner_id': fields.many2one(
            'res.partner', 'From docnaet partner', required=True,
            help='Move all document from this partner to another'),
        'to_partner_id': fields.many2one(
            'res.partner', 'To docnaet partner', required=True,
            help='Destination partner for all document'),
        'status': fields.text('Status'),    
        }
        
    _defaults = {
        'mode': lambda *x: 'customer',
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
