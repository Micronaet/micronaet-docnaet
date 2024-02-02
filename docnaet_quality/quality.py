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

    _columns = {
        'claim_id': fields.many2one('quality.claim', 'Claim'),
        'acceptation_id': fields.many2one(
            'quality.acceptation', 'Acceptation'),
        'sampling_id': fields.many2one('quality.sampling', 'Sampling'),
        'conformed_id': fields.many2one('quality.conformed', 'Conformed'),
        'external_id': fields.many2one(
            'quality.conformed.external', 'Conformed external'),
        'action_id': fields.many2one('quality.action', 'Action'),
        }

class QualityClaim(orm.Model):
    """ Model name: Claims
    """

    _inherit = 'quality.claim'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'claim_id', 'Document'),
        }

class QualityAcceptation(orm.Model):
    """ Model name: acceptation
    """

    _inherit = 'quality.acceptation'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'acceptation_id', 'Document'),
        }

class QualitySampling(orm.Model):
    """ Model name: sampling
    """

    _inherit = 'quality.sampling'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'sampling_id', 'Document'),
        }

class QualityConformed(orm.Model):
    """ Model name: conformed
    """

    _inherit = 'quality.conformed'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'conformed_id', 'Document'),
        }

class QualityConformedExternal(orm.Model):
    """ Model name: conformed
    """

    _inherit = 'quality.conformed.external'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'external_id', 'Document'),
        }

class QualityAction(orm.Model):
    """ Model name: conformed
    """

    _inherit = 'quality.action'

    _columns = {
        'docnaet_ids': fields.one2many(
            'docnaet.document', 'action_id', 'Document'),
        }


# Upload
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

        # ---------------------------------------------------------------------
        # Extra update when product is choosen:
        # ---------------------------------------------------------------------
        # Select current imported:
        document_pool = self.pool.get('docnaet.document')
        domain = res.get('domain')
        document_ids = document_pool.search(cr, uid, domain, context=context)

        # Update with product list data:
        document_pool.write(cr, uid, document_ids, {
            'claim_id': wiz_proxy.claim_id.id,
            'acceptation_id': wiz_proxy.acceptation_id.id,
            'sampling_id': wiz_proxy.sampling_id.id,
            'conformed_id': wiz_proxy.conformed_id.id,
            'external_id': wiz_proxy.external_id.id,
            'action_id': wiz_proxy.action_id.id,
            }, context=context)
        return res

    _columns = {
        'claim_id': fields.many2one('quality.claim', 'Claim'),
        'acceptation_id': fields.many2one(
            'quality.acceptation', 'Acceptation'),
        'sampling_id': fields.many2one('quality.sampling', 'Sampling'),
        'conformed_id': fields.many2one('quality.conformed', 'Conformed'),
        'external_id': fields.many2one(
            'quality.conformed.external', 'Conformed external'),
        'action_id': fields.many2one('quality.action', 'Action'),
        }

# Extra Search
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

        # ---------------------------------------------------------------------
        # Extra Domain:
        # ---------------------------------------------------------------------
        claim_id = current_proxy.claim_id.id or False
        if claim_id:
            domain.append(('claim_id', '=', claim_id))

        acceptation_id = current_proxy.acceptation_id.id or False
        if acceptation_id:
            domain.append(('acceptation_id', '=', acceptation_id))

        sampling_id = current_proxy.sampling_id.id or False
        if sampling_id:
            domain.append(('sampling_id', '=', sampling_id))

        conformed_id = current_proxy.conformed_id.id or False
        if conformed_id:
            domain.append(('conformed_id', '=', conformed_id))

        external_id = current_proxy.external_id.id or False
        if external_id:
            domain.append(('external_id', '=', external_id))

        action_id = current_proxy.action_id.id or False
        if action_id:
            domain.append(('action_id', '=', action_id))

        return res

    _columns = {
        'claim_id': fields.many2one('quality.claim', 'Claim'),
        'acceptation_id': fields.many2one(
            'quality.acceptation', 'Acceptation'),
        'sampling_id': fields.many2one('quality.sampling', 'Sampling'),
        'conformed_id': fields.many2one('quality.conformed', 'Conformed'),
        'external_id': fields.many2one(
            'quality.conformed.external', 'Conformed external'),
        'action_id': fields.many2one('quality.action', 'Action'),
        }

# Duplication:
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
        origin_id = context.get('active_id')
        origin = document_pool.browse(cr, uid, origin_id, context=context)

        domain = res.get('domain')
        destination_ids = document_pool.search(
            cr, uid, domain, context=context)

        # Update with product list data:
        document_pool.write(cr, uid, destination_ids, {
            'claim_id': origin.claim_id.id,
            'acceptation_id': origin.acceptation_id.id,
            'sampling_id': origin.sampling_id.id,
            'conformed_id': origin.conformed_id.id,
            'external_id': origin.external_id.id,
            'action_id': origin.action_id.id,
            }, context=context)
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
