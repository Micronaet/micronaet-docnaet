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


class UlploadDocumentWizard(orm.TransientModel):
    ''' Wizard to upload document
    '''
    _name = 'docnaet.document.upload.wizard'
    _description = 'Document upload'


    def button_personal_folder(self, cr, uid, ids, context=None):
        # TODO complete open folder with agent procedure
        return True

    def button_upload(self, cr, uid, ids, context=None):
        ''' Button event for upload
        '''
        # TODO complete the load from folder:
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        document_pool = self.pool.get('docnaet.document')
        
        # Read document folder and create docunaet.document:
        for loop in range(0,4): # TODO remove loop (testing)
            data = {
                'name': 'document %s' % loop,
                'protocol_id': wiz_proxy.default_protocol_id.id or False,
                'user_id': wiz_proxy.default_user_id.id or uid, 
                'partner_id': wiz_proxy.default_partner_id.id or 1, 
                'language_id': wiz_proxy.default_language_id.id or False, 
                'type_id': wiz_proxy.default_type_id.id or False,
                'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'import_date': datetime.now().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'uploaded': True,
                }
            document_pool.create(cr, uid, data, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': [
                ('user_id', '=', uid), 
                ('uploaded', '=', True), 
                ('state', '=', 'draft')],
            'type': 'ir.actions.act_window',
            # TODO create a view for direct writing and a button for open form
            #'res_id': document_id,  # IDs selected
        }

    _columns = {
        'default_partner_id': fields.many2one(
            'res.partner', 'Default partner'),
        'assign_protocol': fields.boolean('Assign protocol'),    
        'default_user_id': fields.many2one('res.users', 
            'Default user'),
        'default_protocol_id': fields.many2one('docnaet.protocol', 
            'Default protocol'),
        'default_type_id': fields.many2one('docnaet.type', 
            'Default type'),            
        'default_language_id': fields.many2one('docnaet.language', 
            'Default language'),
        'folder_status': fields.text('Folder status')
        }

    _defaults = {
        'default_user_id': lambda s, cr, uid, ctx: uid,
        # TODO: default function
        'folder_status': lambda *x: '''
                <style>
                    .table_bf {
                         border:1px 
                         padding: 3px;
                         solid black;
                     }
                    .table_bf td {
                         border:1px 
                         solid black;
                         padding: 3px;
                         text-align: center;
                     }
                    .table_bf th {
                         border:1px 
                         solid black;
                         padding: 3px;
                         text-align: center;
                         background-color: grey;
                         color: white;
                     }
                </style>
            <p> 
                <table class="table_bf">
                    <tr>
                        <td>&nbsp;Date&nbsp;</td>
                        <td>&nbsp;File name&nbsp;</td>
                        <td>&nbsp;Ext.&nbsp;</td>
                    </tr>
                    <tr>
                        <td>TODO 23/12/1972 11:00:00</td>
                        <td>Offerta XXX</td>
                        <td>DOC</td>
                    </tr>
                </table>
            </p>'''
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
