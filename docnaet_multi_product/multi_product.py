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

class DocnaetDocumentRequest(orm.Model):
    """ Model name: Docnaet Document Requests
    """

    _name = 'docnaet.document.request'
    _order = 'name'

    def mark_as_undone(self, cr, uid, ids, context=None):
        """ Mark as undone
        """
        return self.write(cr, uid, ids, {
            'done': False,
            }, context=context)

    def mark_as_done(self, cr, uid, ids, context=None):
        """ Mark as done
        """
        return self.write(cr, uid, ids, {
            'done': True,
            }, context=context)

    _columns = {
        'user_id': fields.many2one('res.users', 'Richiedente'),
        'partner_id': fields.many2one(
            'res.partner', 'Fornitore', required=True),
        'name': fields.char('Descrizione richiesta', size=80),
        'supplier_code': fields.char('Codice fornitore', size=80),
        'request_date': fields.date('Data richiesta'),
        'note': fields.text('Note'),
        'done': fields.boolean('Chiusa'),
        }

    _defaults = {
        'user_id': lambda s, cr, uid, ctx: uid,
        'request_date': lambda *x: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
        }

class DocnaetDocument(orm.Model):
    """ Model name: DocnaetDocument
    """

    _inherit = 'docnaet.document'

    _columns = {
        'product_prefilter': fields.char('Filtro prodotto', size=60),
        'supplier_code': fields.char('Codice fornitore', size=64),
        'docnaet_product_ids': fields.many2many(
            'product.product', 'docnaet_multi_product_rel',
            'docnaet_id', 'product_id',
            'Products'),
        }

class ProductProduct(orm.Model):
    """ Model name: DocnaetDocument
    """

    _inherit = 'product.product'

    _columns = {
        'product_docnaet_ids': fields.many2many(
            'docnaet.document', 'docnaet_multi_product_rel',
            'product_id', 'docnaet_id',
            'Document'),
        }

class DocnaetDocumentAdvancedSearchWizard(orm.TransientModel):
    """ Wizard for duplicate model
    """
    _inherit = 'docnaet.document.advanced.search.wizard'

    def advanced_search(self, cr, uid, ids, context=None):
        """ Override search function add product:
        """
        res = super(DocnaetDocumentAdvancedSearchWizard, self).advanced_search(
            cr, uid, ids, context=context)

        domain = res.get('domain')
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        product_id = current_proxy.docnaet_product_id.id or False
        supplier_code = current_proxy.supplier_code
        if product_id:
            domain.append(('docnaet_product_ids.id', '=', product_id))
        if supplier_code:
            domain.append(('supplier_code', 'ilike', supplier_code))

        return res

    _columns = {
        'supplier_code': fields.char('Codice fornitore', size=64),
        'docnaet_product_id': fields.many2one('product.product', 'Product'),
        }


class UploadDocumentWizard(orm.TransientModel):
    """ Wizard to upload document
    """
    _inherit = 'docnaet.document.upload.wizard'

    def button_upload(self, cr, uid, ids, context=None):
        """ Button event for upload
        """
        res = super(UploadDocumentWizard, self).button_upload(
            cr, uid, ids, context=context)

        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        if not wiz_proxy.docnaet_product_ids and not wiz_proxy.supplier_code:
            return res

        # ---------------------------------------------------------------------
        # Extra update when product is choosen:
        # ---------------------------------------------------------------------
        docnaet_product_ids = [
            item.id for item in wiz_proxy.docnaet_product_ids]

        # Select current imported:
        document_pool = self.pool.get('docnaet.document')
        domain = res.get('domain')
        document_ids = document_pool.search(cr, uid, domain, context=context)

        # Update with product list data:
        document_pool.write(cr, uid, document_ids, {
            'supplier_code': wiz_proxy.supplier_code,
            'docnaet_product_ids': [(6, 0, docnaet_product_ids)],
            }, context=context)
        return res

    _columns = {
        'supplier_code': fields.char('Codice fornitore', size=64),
        'docnaet_product_ids': fields.many2many(
            'product.product', 'docnaet_multi_product_wiz_rel',
            'wiz_id', 'product_id',
            'Products'),
        }


class DocumentDuplication(orm.TransientModel):
    """ Wizard for duplicate model
    """
    _inherit = 'docnaet.document.duplication.wizard'

    def duplicate_operation(self, cr, uid, ids, mode='link', context=None):
        """ Override for write product in new
        """
        res = super(DocumentDuplication, self).duplicate_operation(
            cr, uid, ids, mode=mode, context=context)

        # Update duplicated with original extra data:
        document_pool = self.pool.get('docnaet.document')
        original_id = context.get('active_id')
        original = document_pool.browse(cr, uid, original_id, context=context)
        if not original.docnaet_product_ids:
            return res

        docnaet_product_ids = [
            item.id for item in original.docnaet_product_ids]

        domain = res.get('domain')
        destination_ids = document_pool.search(
            cr, uid, domain, context=context)

        # Update with product list data:
        document_pool.write(cr, uid, destination_ids, {
            'docnaet_product_ids': [(6, 0, docnaet_product_ids)],
            }, context=context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
