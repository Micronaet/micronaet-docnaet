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
import shutil
from openerp.osv import osv, orm, fields
from datetime import datetime
from datetime import datetime, timedelta
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class docnaet_document_advanced_search_wizard(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _name = 'docnaet.document.advanced.search.wizard'
    _description = 'Advanced search'

    def advanced_search(self, cr, uid, ids, context=None):
        ''' Advanced search
        '''
        assert len(ids) == 1, 'Works only with one record a time'
            
        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        domain = []
        keywords = current_proxy.keywords or False
        partner_name = current_proxy.partner_name or False
        
        if keywords:
            for key in keywords.split(): 
                domain.append(('name', 'ilike', key))      
        if partner_name:
            domain.append(('partner_id.name', 'ilike', partner_name))

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': domain,
            'type': 'ir.actions.act_window',
            #'res_id': destination_id,  # IDs selected
            }

    _columns = {
        'keywords': fields.char('Keywords', size=80),
        'partner_name': fields.char('Partner name', size=80),
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: