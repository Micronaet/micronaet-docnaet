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


class document_import(orm.TransientModel):
    ''' Wizard for duplicate model
    '''
    _name = 'docnaet.document.import.wizard'
    _description = 'Document import'


    def document_folder(self, cr, uid, ids, context=None):
        ''' Button open personal folder
        '''
        url = 'docnaet://[home]%s' % uid
        import pdb; pdb.set_trace()
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
        import pdb; pdb.set_trace()
        # Clean current draft document for user
        
        # Read file in user folder
        
        # Create document in draft for user
        
        # Redirect to tree view:
        return {
            #'view_type': 'form',
            #'view_mode': 'tree,form,calendar',
            #'res_model': 'docnaet.document',
            #'domain': [('id', '=', document_id)],
            #'type': 'ir.actions.act_window',
            #'res_id': document_id,  # IDs selected
        }

    _columns = {
        }

    _defaults = {
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
