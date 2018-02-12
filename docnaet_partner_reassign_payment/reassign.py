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

class DocnaetPartnerReassignEventWizard(orm.TransientModel):
    ''' Wizard for reassign partner
    '''
    _inherit = 'docnaet.partner.reassign.wizard'

    def get_no_docnaet_partner_with_payment(self, cr, uid, ids, context=None):
        ''' Return partner with no docnaet document but payment
        '''
        query = '''
            SELECT id from res_partner 
            WHERE 
                id IN (
                    SELECT partner_id FROM sql_payment_duelist) AND
                id NOT IN (
                    SELECT partner_id FROM docnaet_document);            
            '''            
        cr.execute(query)
        partner_ids = [item.id for item in cr.fetchall()]    
        if not partner_ids:
            raise osv.except_osv(
                _('Error'), 
                _('No partner present in payment and not in Docnaet'),
                )
                
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(
            cr, uid, 
            'docnaet_partner_reassign', 
            'view_res_partner_no_docnaet_tree',
            )[1]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partner with duelist but not docnaet document'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': view_id, # False
            'views': [(view_id, 'tree'), (False, 'form')],
            'domain': [('id', 'in', partner_ids)],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
class SqlPaymentSuelist(orm.Model):
    """ Model name: SqlPaymentSuelist
    """
    
    _inherit = 'sql.payment.duelist'

    def docnaet_partner_reassign_this(self, cr, uid, ids, context=None):
        ''' Open wizard with detault partner
        '''
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(
            cr, uid, 
            'docnaet_partner_reassign', 
            'docnaet_partner_reassign_wizard_view')[1]    
            
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Change docnaet partner'),
            'view_type': 'form',
            'view_mode': 'form',
            #'res_id': 1,
            'res_model': 'docnaet.partner.reassign.wizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'domain': [],
            'context': {'default_to_partner_id': current_proxy.partner_id.id},
            'target': 'new',
            #'nodestroy': False,
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
