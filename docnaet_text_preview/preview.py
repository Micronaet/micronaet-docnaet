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
from openerp import SUPERUSER_ID#, api
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
    
    def document_text_preview(self, cr, uid, ids, context=None):
        ''' Return document preview
        '''
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(
            cr, uid, 
            'docnaet_text_preview', 
            'view_document_text_preview_form',
            )[1]
    
        return {
            'type': 'ir.actions.act_window',
            'name': _('Text preview'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'docnaet.document',
            'view_id': view_id, # False
            'views': [(view_id, 'form')],
            'domain': [],
            'context': context,
            'target': 'new',
            'nodestroy': False,
            }
            
    def _get_text_preview_of_document(
            self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        company_pool = self.pool.get('res.company')
        res = {}
        for document in self.browse(cr, uid, ids, context=context):
            filename = self.get_document_filename(
                cr, uid, document, mode='filename', context=context)
            fullname = self.get_document_filename(
                cr, uid, document, mode='fullname', context=context)
                
            res[document.id] = company_pool.document_parse_doc_to_text(
                filename, fullname)
        return res
        
    _columns = {
        'text_preview': fields.function(
            _get_text_preview_of_document, method=True, 
            type='text', string='Text preview', 
            store=False),                         
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
