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


class UploadDocumentWizard(orm.TransientModel):
    ''' Wizard to upload document
    '''
    _name = 'docnaet.document.upload.wizard'
    _description = 'Document upload'

    def onchange_country_partner_domain(self, cr, uid, ids, partner_name,
            country_id, 
            #category_id, 
            context=None):
        ''' On change for domain purpose
        '''
        res = {}
        res['domain'] = {'default_partner_id': [
            ('docnaet_enable', '=', True),
            ]}        
        
        if country_id:
            res['domain']['default_partner_id'].append(
                ('country_id', '=', country_id),
                )
        if partner_name:
            if '+' in partner_name:
                partner_part = partner_name.split('+')
                res['domain']['default_partner_id'].extend([
                    ('name', 'ilike', p) for p in partner_part])
            else:   
                res['domain']['default_partner_id'].append(
                    ('name', 'ilike', partner_name),
                    )
                
        #if category_id:
        #    res['domain']['partner_id'].append(
        #        ('docnaet_category_id','=', category_id),
        #        )
        _logger.warning('Filter: %s' % res)
        return res

    def private_listdir(self, cr, uid, context=None):
        ''' Return private listdir list
        '''
        res = []
        
        company_pool = self.pool.get('res.company')
        private_folder = company_pool.get_docnaet_folder_path(
            cr, uid, subfolder='user', context=context)
        
        for f in os.listdir(private_folder):
            try:
                fullpath = os.path.join(private_folder, f)
            except:
                raise osv.except_osv(
                    _('File upload'), 
                    _('Change file name, character not permit: %s' % f),
                    )    
            if not os.path.isfile(fullpath):
                continue
            res.append((fullpath, f))          
        return res                

    def button_personal_folder(self, cr, uid, ids, context=None):
        # TODO complete open folder with agent procedure
        document_pool = self.pool.get('docnaet.document')
        return document_pool.call_docnaet_url(
            cr, uid, ids, mode='home', context=context)

    def button_reassign(self, cr, uid, ids, context=None):
        ''' Button reassign wizard
        '''
        if context is None:
            context = {}
        active_ids = context.get('active_ids', [])    
        if not active_ids:
            raise osv.except_osv(
                _('No selection'), 
                _('Select document to reassign'),
                )
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        if current_proxy.default_partner_id:
            data['partner_id'] = current_proxy.default_partner_id.id
        if current_proxy.default_user_id:
            data['user_id'] = current_proxy.default_user_id.id
        if current_proxy.default_protocol_id:
            data['protocol_id'] = current_proxy.default_protocol_id.id
        # TODO manage: assign protocol!
        
        if current_proxy.default_type_id:
            data['type_id'] = current_proxy.default_type_id.id
        if current_proxy.default_language_id:
            data['language_id'] = current_proxy.default_language_id.id
        
        document_pool = self.pool.get('docnaet.document')
        document_pool.write(cr, uid, active_ids, data, context=context)  

        # Reassign protocol number:    
        if current_proxy.assign_protocol:
            document_pool.assign_protocol_number(
                cr, uid, active_ids, context=context)
        # TODO reassign_confirm for change status in confirmed
        
        model_pool = self.pool.get('ir.model.data')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reassign characteristics'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'docnaet.document',
            #'view_id': view_id, # Fale
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', active_ids)],
            'context': context,
            'target': 'current',
            'nodestroy': False,
            }      
        
    def button_upload(self, cr, uid, ids, context=None):
        ''' Button event for upload
        '''
        if context is None:
            context = {}

        # TODO complete the load from folder:
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        file_mode = wiz_proxy.file_mode 

        # Partial mode
        file_selected = []

        if file_mode == 'partial':
            file_selected = [
                item.name for item in wiz_proxy.document_ids if item.to_import]
        
        company_pool = self.pool.get('res.company')
        document_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        program_pool = self.pool.get('docnaet.protocol.template.program')

        doc_proxy = self.browse(cr, uid, ids, context=context)[0]
        
        # Difference between Docnaet and Labnaet:
        docnaet_mode = doc_proxy.docnaet_mode
        if not docnaet_mode:
            raise osv.except_osv(
                _('Docnaet mode:'), 
                _('Cannot find document mode (labnaet or docnaet'),
                )
        context['docnaet_mode'] = docnaet_mode

        # ---------------------------------------------------------------------        
        # Folder depend on doc/lab mode
        # ---------------------------------------------------------------------        
        # Store (output):
        store_folder = company_pool.get_docnaet_folder_path(
            cr, uid, subfolder='store', context=context)
        
        # Private (input):
        private_folder = self.private_listdir(cr, uid, context=context)

        for fullpath, f in private_folder:
            if file_mode == 'partial' and f not in file_selected:
                continue # jumped
            
            # -----------------------------------------------------------------
            # Create record for document:
            # -----------------------------------------------------------------  
            extension = f.split('.')[-1].lower()
            if len(extension) > 4:
                _logger.warning(
                    _('Extension must be <= 4 char (jump file %s!') % f)
                continue

            if docnaet_mode == 'labnaet':
                labnaet_id = document_pool.get_counter_labnaet_id(
                    cr, uid, context=context)
            else:
                labnaet_id = False
        
            data = {
                'docnaet_mode': docnaet_mode,
                'labnaet_id': labnaet_id,
                'name': 'Document %s' % f,
                'protocol_id': wiz_proxy.default_protocol_id.id or False,
                'user_id': wiz_proxy.default_user_id.id or uid, 
                'partner_id': wiz_proxy.default_partner_id.id or False, 
                'language_id': wiz_proxy.default_language_id.id or False, 
                'type_id': wiz_proxy.default_type_id.id or False,
                'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'import_date': datetime.now().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT),
                'uploaded': True,
                'docnaet_extension': extension,
                'program_id': program_pool.get_program_from_extension(
                    cr, uid, extension, context=context)
                }
            if wiz_proxy.assign_protocol:
                data['number'] = protocol_pool.assign_protocol_number(
                    cr, uid, data['protocol_id'], context=context)                
            item_id = document_pool.create(cr, uid, data, context=context)

            # -----------------------------------------------------------------
            # Labnaet alternative:
            # -----------------------------------------------------------------
            # ID mode labnaet / docnaet (force labnaet_id):
            if docnaet_mode == 'labnaet':
                item_id = labnaet_id

            # -----------------------------------------------------------------
            # Import file in store:
            # -----------------------------------------------------------------
            fullstore = '%s.%s' % (
                os.path.join(store_folder, str(item_id)),
                extension,
                )
            os.rename(fullpath, fullstore)

            try:            
                os.system('chown openerp7:openerp7 %s' % fullstore)
                os.system('chmod 775 %s' % fullstore)
                _logger.info('Change permission to new file')
            except:
                _logger.error('Cannot set property of file')

        context['default_docnaet_mode'] = docnaet_mode
        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': [
                ('docnaet_mode', '=', docnaet_mode),
                ('user_id', '=', uid), 
                ('uploaded', '=', True), 
                ('state', '=', 'draft'),
                ],
            'type': 'ir.actions.act_window',
            'context': context,
            }

    def default_read_upload_folder(
            self, cr, uid, mode='html', context=None):
        ''' Read folder and return html text
        '''
        if context is None:
            context = {}
        docnaet_mode = context.get('docnaet_mode', 'docnaet')    
        
        if mode == 'html':
            res = ''
        else:
            res = []

        # Get private folder:        
        private_folder = self.private_listdir(cr, uid, context=context)
        for fullpath, f in private_folder:
            ts = datetime.fromtimestamp(
                os.path.getmtime(fullpath)).strftime('%Y/%m/%d')
            ts = ts.replace('/', '-')
            if mode == 'html':
                res += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                    f, ts, f.split('.')[-1])

            else: # mode default one2many
                res.append((0, 0, {
                    'to_import': False,
                    'name': f,
                    'date': ts,
                    'fullname': fullpath,
                    }))  
                              
        if mode == 'html':        
            return '''
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
                        %s
                    </table>
                </p>''' % res
        else:
            return res    
        
    
    _columns = {
        'mode': fields.selection([
            ('upload', 'Upload mode'),
            ('reassign', 'Reassign mode'),
            ], 'Mode'),            

        # Filter for partner:
        'partner_name': fields.char('Partner name', size=80),
        'country_id': fields.many2one('res.country', 'Country'),
            
        'default_partner_id': fields.many2one(
            'res.partner', '>> Default partner',
            domain=[('docnaet_enable', '=', True)],
            ),
        'assign_protocol': fields.boolean('Assign protocol', 
            help='In upload mode assign protocol and next number'),    
        'default_user_id': fields.many2one('res.users', 
            'User'),
        'default_protocol_id': fields.many2one(
            'docnaet.protocol', 'Protocol', 
            domain=[('invisible', '=', False)],
            ),
        'default_type_id': fields.many2one('docnaet.type', 
            'Type'),            
        'default_language_id': fields.many2one('docnaet.language', 
            'Language'),
        'folder_status': fields.text('Folder status'),
        'reassign_confirm': fields.boolean('Confirm after reassign',
            help='After reassign feature confirm all draft elements'),
        'file_mode': fields.selection([
            ('all', 'All'),
            ('partial', 'Partial'),
            ], 'File mode'),
        'docnaet_mode': fields.selection([
            ('docnaet', 'Docnaet'), # Only for docnaet
            ('labnaet', 'Labnaet'),
            #('all', 'All'),
            ], 'Docnaet mode', required=True,
            help='Usually document management, but for future improvement also'
                ' for manage other docs'),
        }

    _defaults = {
        'docnaet_mode': lambda *x: 'docnaet',
        'mode': lambda *x: 'upload',
        'default_user_id': lambda s, cr, uid, ctx: uid,
        'folder_status': lambda s, cr, uid, ctx: s.default_read_upload_folder(
            cr, uid, context=ctx), 
        'file_mode': lambda *x: 'all',
        }

class UploadDocumentFile(orm.TransientModel):
    ''' Wizard to upload document
    '''
    _name = 'docnaet.document.upload.file'
    _description = 'Document upload file'

    _columns = {
        'to_import': fields.boolean('Import'),
        'name': fields.char('File name', size=100, required=True, 
            readonly=True),
        'fullname': fields.char('Full name', size=400),
        'date': fields.date('Time stamp'),
        'wizard_id': fields.many2one(
            'docnaet.document.upload.wizard', 'Wizard'),
        }
        
class UploadDocumentWizard(orm.TransientModel):
    ''' Wizard to upload document
    '''
    _inherit = 'docnaet.document.upload.wizard'
    
    def get_default_file_ids(self, cr, uid, context=None):
        ''' Load user files directly
        '''        
        if context is None:
            context = {}
            
        res = self.default_read_upload_folder(
            cr, uid, mode='o2m', context=context)
        return res

    _columns = {
        'document_ids': fields.one2many(
            'docnaet.document.upload.file', 'wizard_id', 'Files'),
        }
    
    _defaults = {
        'document_ids': lambda s, cr, uid, ctx: s.get_default_file_ids(
            cr, uid, context=ctx),
        }    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
