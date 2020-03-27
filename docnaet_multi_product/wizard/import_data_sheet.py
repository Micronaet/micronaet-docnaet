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

class docnaet_import_datasheet_wizard(orm.TransientModel):
    ''' Wizard for import datasheet
    '''
    _name = 'docnaet.import.datasheet.wizard'
    _description = 'Import datasheet'

    def import_operation(self, cr, uid, ids, context=None):
        ''' Import management
        '''
        assert len(ids) == 1, 'Works only with one record a time'
            
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        import pdb; pdb.set_trace()
        
        default_path = wiz_proxy.default_path
        filename = wiz_proxy.filename
        
        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        partner_pool = self.pool.get('res.partner')

        if filename:
            files = [filename]
        else:                 
            for root, folders, files in os.walk(path)
                break  # Update files list only with current folder

        import pdb; pdb.set_trace()
        log_text = ''            
        for f in files:
            if f.split('.')[-1] not in ('xls', 'xlsx'):
                log_text.append('File not used: %s\n' % f)
                continue
            else:
                log_text.append('File used: %s\n' % f)
                
            xls_file = os.path.join(path, f)        
            wb = xlrd.open_workbook(xls_file)
            for ws_name in wb.sheet_names():
                ws = wb.sheet_by_name(ws_name)
                for position in ws.hyperlink_map:
                    row, col = position
                    try:
                        cell = ws.cell(row, col)
                    except:
                        print 'Cell not found', f, ws_name, row, col
                        continue
                    
                    link = ws.hyperlink_map[position]
                    if link.type != 'url':
                        continue

                    file_link = os.path.join(path, link.url_or_path)
                    print ws_name, row, col, cell.value, file_link
                                
    _columns = {
        'default_path': fields.char('Default path', size=180, required=True),
        'filename': fields.char('File name', size=180),
        }

