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
import openerp.netsvc as netsvc
from openerp.osv import osv, orm, fields
from datetime import datetime, timedelta
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

class DocnaetGdocDocument(orm.Model):
    """ Model name: Docnaet document
    """
    
    _inherit = 'docnaet.document'
    
    # Override open document:
    def call_docnaet_url(self, cr, uid, ids, mode, remote=False, context=None):        
        """ Override open document
        """
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        url = current_proxy.gdoc_link
        if url:
            return {
                'name': 'Open as G-Doc',
                #res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url', 
                'url': url, 
                'target': 'new',
                }
            
        else:  # Normal link:
            return super(DocnaetGdocDocument, self).call_docnaet_url(
                cr, uid, ids, mode, remote=remote, context=context)    
        
    _columns = {
        'gdoc_link': fields.char('Cloud Link', size=480),
        }
    
