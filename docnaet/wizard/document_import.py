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
from openerp.osv import osv, orm, fields
from datetime import datetime
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)



class document_import(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _name = 'docnaet.document.import.wizard'
    _description = 'Document import'


    def document_folder(self, cr, uid, ids, context=None):
        ''' Button open personal folder
        '''
        url = 'docnaet://[home]%s' % uid
        return {
          'name': 'User folder',
          'res_model': 'ir.actions.act_url',
          'type': 'ir.actions.act_url',
          #'target': 'current',
          'url': url,
           }    
           
    def document_import(self, cr, uid, ids, context=None):
        ''' Button event for duplication
        '''
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        
        # ---------------------------------------------------------------------
        # Clean current draft document for user
        # ---------------------------------------------------------------------
        doc_pool = self.pool.get('docnaet.document')
        
        # Search my draft document
        doc_ids = doc_pool.search(cr, uid, [
            ('user_id', '=', uid),
            ('state', '=', 'draft'), 
            ('imported', '=', True),
            ], context=context)
        
        # Unlink document
        doc_pool.unlink(cr, uid, doc_ids, context=context)
        
        # ---------------------------------------------------------------------
        # Read file in user folder
        # ---------------------------------------------------------------------
        path = '/home/thebrush/temp/Gloria' # TODO
        filelist = [f for f in listdir(path) if isfile(join(path, f))]

        # ---------------------------------------------------------------------
        # Create document in draft for user
        # ---------------------------------------------------------------------
        docnaet_ids = []
        for f in filelist:
            doc_id = doc_pool.create(cr, uid, {
                'name': f,
                'filename': f, 
                'user_id': uid,
                'partner_id': 1,
                'imported': True,
                #'protocol_id': 1,
                }, context=context)
            docnaet_ids.append(doc_id)    
        
        # ---------------------------------------------------------------------
        # Redirect to tree view:
        # ---------------------------------------------------------------------
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': [('id', 'in', docnaet_ids)],
            'type': 'ir.actions.act_window',
            #'res_id': document_id,  # IDs selected
            }

    _columns = {
        }

    _defaults = {
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
