#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
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

class DocnaetDocument(orm.Model):
    """ Model name: DocnaetDocument
    """
    
    _inherit = 'docnaet.document'

    # Override action partner_id hided
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
            if not current_proxy.partner_ids:
                raise osv.except_osv(
                    _('Partner'), 
                    _('No partner assigned, choose one before and confirm!'),
                    )
            data['number'] = protocol_pool.assign_protocol_number(
                cr, uid, protocol.id, context=context)
        return self.write(cr, uid, ids, data, context=context)

    _columns = {
        'docnaet_partner_ids': fields.many2many(
            'res.partner', 'docnaet_multi_partner_rel', 
            'docnaet_id', 'partner_id', 
            'Partner', domain="[('docnaet_enable', '=', True)]"),
        }

class ResPartner(orm.Model):
    """ Model name: DocnaetDocument
    """
    
    _inherit = 'res.partner'
    
    _columns = {
        'partner_docnaet_ids': fields.many2many(
            'docnaet.document', 'docnaet_multi_partner_rel', 
            'partner_id', 'docnaet_id', 
            'Document'),
        }


class DocnaetDocumentAdvancedSearchWizard(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _inherit = 'docnaet.document.advanced.search.wizard'

    def advanced_search(self, cr, uid, ids, context=None):
        ''' Override search function add product:
        '''
        res = super(DocnaetDocumentAdvancedSearchWizard, self).advanced_search(
            cr, uid, ids, context=context)

        domain = res.get('domain')
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        partner_id = current_proxy.docnaet_partner_id.id or False
        if partner_id:
            domain.append(('docnaet_partner_ids.id', '=', partner_id))
        return res
    
    _columns = {
        'docnaet_partner_id': fields.many2one('res.partner', 'Partner'),
        }       

class UploadDocumentWizard(orm.TransientModel):
    ''' Wizard to upload document
    '''
    _inherit = 'docnaet.document.upload.wizard'
    
    def button_upload(self, cr, uid, ids, context=None):
        ''' Button event for upload
        '''
        res = super(UploadDocumentWizard, self).button_upload(
            cr, uid, ids, context=context)
        
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        if not wiz_proxy.docnaet_partner_ids:
            return res

        # ---------------------------------------------------------------------
        # Extra update when partner is choosen:    
        # ---------------------------------------------------------------------
        docnaet_partner_ids = [
            item.id for item in wiz_proxy.docnaet_partner_ids]
        
        # Select current imported:
        document_pool = self.pool.get('docnaet.document')
        domain = res.get('domain')
        document_ids = document_pool.search(cr, uid, domain, context=context)
        
        # Update with partner list data:
        document_pool.write(cr, uid, document_ids, {
            'docnaet_partner_ids': [(6, 0, docnaet_partner_ids)],
            }, context=context)
        return res    

    _columns = {
        'docnaet_partner_ids': fields.many2many(
            'res.partner', 'docnaet_multi_partner_wiz_rel', 
            'wiz_id', 'partner_id', 
            'Partner', domain="[('docnaet_enable', '=', True)]"),
        }     

class DocumentDuplication(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _inherit = 'docnaet.document.duplication.wizard'

    def duplicate_operation(self, cr, uid, ids, mode='link', context=None):
        ''' Override for write partner in new
        '''
        res = super(DocumentDuplication, self).duplicate_operation(
            cr, uid, ids, mode=mode, context=context)

        # Update duplicated with original extra data:
        document_pool = self.pool.get('docnaet.document')
        original_id = context.get('active_id')
        original = document_pool.browse(cr, uid, original_id, context=context)
        if not original.docnaet_partner_ids:
            return res

        docnaet_partner_ids = [
            item.id for item in original.docnaet_partner_ids]

        domain = res.get('domain')
        destination_ids = document_pool.search(
            cr, uid, domain, context=context)
        
        # Update with partner list data:
        document_pool.write(cr, uid, destination_ids, {
            'docnaet_partner_ids': [(6, 0, docnaet_partner_ids)],
            }, context=context)
        return res    
                                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
