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

class ResCountryUniqueNameWizard(orm.TransientModel):
    ''' Wizard for unify country with name
    '''
    _name = 'res.country.unique.name.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def unify_country(self, cr, uid, ids, context=None):
        ''' Search partner not used
            Try to unify other
        '''
        _logger.info('Start unify country:')
        if context is None:
            context = {}
        country_pool = self.pool.get('res.country')        
            
        
        # ---------------------------------------------------------------------
        # Get old and new value:
        # ---------------------------------------------------------------------
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        new_country_id = current_proxy.new_country_id.id
        old_country_ids = context.get('active_ids', False)

        # Check fields:        
        if not new_country_id or not old_country_ids:
            raise osv.except_osv(
                _('No selection'), 
                _('Select one or more elements to unify'),
                ) 

        # ---------------------------------------------------------------------
        # Reassign procedure:
        # ---------------------------------------------------------------------
        query_db = ( 
            # XXX current linked foreign keys of res_country table
            ('crm_lead', 'country_id'),
            ('crm_trip', 'country_id'),
            ('delivery_grid_country_rel', 'country_id'),
            ('docnaet_document', 'country_id'),
            ('portal_crm_crm_contact_us', 'country_id'),
            ('res_bank', 'country'),
            ('res_country_state', 'country_id'),
            ('res_partner_bank', 'country_id'),
            ('res_partner', 'country_id'),
            ('res_region', 'country_id'),
            ('sql_payment_duelist', 'country_id'),
            )            
        
        error = False
        for table, field in query_db:
            query = 'UPDATE %s SET %s = %s WHERE %s in %s;' % (
                table, 
                field, 
                new_country_id, 
                field, 
                tuple(old_country_ids), 
                )
            query = query.replace(',)', ')')    
            try:    
                _logger.info(query)
                cr.execute(query)                
            except:
                error = True
                _logger.error('%s %s' % (table, field))

        # Remove old country:
        # TODO after testing:
        if not error:
            country_pool.unlink(cr, uid, old_country_ids, context=context) 
        return True
        
    _columns = {
        'new_country_id': fields.many2one(
            'res.country', 'New country', required=True),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
