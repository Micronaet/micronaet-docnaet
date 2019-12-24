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

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
