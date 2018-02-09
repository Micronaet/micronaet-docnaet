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
    def onchange_partner_element(self, cr, uid, from_id, customer_id, 
            supplier_id, context=None):
        ''' Update a status field for get informations
        '''
        res = {}
        return res    
        
    # -------------------------------------------------------------------------
    # Wizard button event:
    # -------------------------------------------------------------------------
    def action_done(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        
        
        wizard_browse = self.browse(cr, uid, ids, context=context)[0]
        
        return {
            'type': 'ir.actions.act_window_close'
            }

    _columns = {
        'mode': fields.selection([
            ('customer', 'Account customer'),
            ('supplier', 'Account supplier'),            
            ], 'Mode', required=True),                
        'from_partner_id': fields.many2one(
            'res.partner', 'From docnaet partner', 
            help='Move all document from this partner to another'),
        'to_customer_id': fields.many2one(
            'res.partner', 'To docnaet partner', 
            help='Destination partner for all document'),
        'status': fields.text('Status'),    
        }
        
    _defaults = {
        'mode': lambda *x: 'customer',
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
