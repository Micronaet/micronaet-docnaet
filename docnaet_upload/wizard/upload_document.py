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
from openerp.osv import osv, orm, fields
from datetime import datetime


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
        # TODO complete with file events:
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        document_pool = self.pool.get('docnaet.document')
        
        # Read document folder and create docunaet.document:
        
        
        data = {
            'name': document_proxy.name, 
            }
        document_id = document_pool.create(cr, uid, data, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': [('user_id', '=', uid), ('uploaded', '=', True)],
            'type': 'ir.actions.act_window',
            #'res_id': document_id,  # IDs selected
        }

    _columns = {
        'default_partner_id': fields.many2one(
            'res.partner', 'Default partner'),
        'assign_protocol': fields.boolean('Assign protocol'),    
        'default_protocol_id': fields.many2one('docnaet.protocol', 
            'Default protocol'),
        'default_type_id': fields.many2one('docnaet.type', 
            'Default type'),            
        'folder_status': fields.text('Folder status')
        }

    _defaults = {
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
                        <td>Date</td><td>File name</td><td>Ext.</td>
                    </tr>
                </table>
            </p>'''
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
