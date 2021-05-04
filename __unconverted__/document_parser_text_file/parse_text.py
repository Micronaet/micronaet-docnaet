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

class FileDocument(orm.Model):
    """ Model name: FileDocument
    """    
    _name = 'file.document'
    _description = 'File document'
    _rec_name = 'name'
    _order = 'name'
    
    def schedule_load_file_list(
            self, cr, uid, path, doc_filter, unlink=True, period=False, context=None):
        ''' Load path passed and create file as record
        '''
        # Pool used:
        company_pool = self.pool.get('res.company')
        _logger.info('Start import file: folder [%s] extension [%s]' % (
             path, doc_filter))
             
        path = os.path.expanduser(path)
        path_len = len(path)
        if period:
            period_date = datetime.now() - timedelta(days=period)
            period_date = period_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if unlink:
            unlink_db = {}
            unlink_ids = self.search(cr, uid, [], context=context)
            for f in self.browse(cr, uid, unlink_ids, context=context): 
                unlink_db[f.fullname] = f.id
                
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                extension = company_pool.get_file_extension(filename)
                if extension not in doc_filter:
                    _logger.warning('Wrong extension: %s' % filename)
                    continue
                fullname = os.path.join(dirpath, filename)
                content = company_pool.document_parse_doc_to_text(
                    filename, fullname) 
                if not content: 
                    _logger.warning('Empty file: %s' % fullname)
                    continue 
                    
                # Get partner and agent information from master folder:
                try:                
                    master_folder = dirpath[path_len:].split('/')[1]
                    if '(' in master_folder:
                        master_list = master_folder.split('(')
                        partner_name = master_list[0].strip()
                        agent_name = master_list[-1].split(')')[0].strip()
                    else:
                        partner_name = master_folder.strip()
                        agent_name = False
                except: # File in root folder dont' have mater folder
                    partner_name = False
                    agent_name = False                 
                
                # Remove fullname from unlink
                if unlink and fullname in unlink_db:
                    del(unlink_db[fullname])
                    
                # Create / update record:
                file_create = datetime.fromtimestamp(
                    os.path.getctime(fullname)).strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)
                file_modify = datetime.fromtimestamp(
                    os.path.getmtime(fullname)).strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)
                if period and file_modify < period_date:
                    _logger.info('Jump file (date file %s < %s): %s' % (
                         file_modify, period_date, filename))
                    continue    
                data = { 
                    'name': filename,
                    'fullname': fullname,
                    'partner_name': partner_name,
                    'agent_name': agent_name,
                    'content': content, 
                    'file_create': file_create,
                    'file_modify': file_modify,                        
                    }
            
                file_ids = self.search(cr, uid, [ # TODO remove use unlink_db
                    ('fullname', '=', fullname), 
                    ], context=context)                 
                if file_ids:
                    self.write(cr, uid, file_ids, data, context=context)
                    _logger.info('Updated: %s' % fullname)
                else:
                    self.create(cr, uid, data, context=context)
                    _logger.info('Created: %s' % fullname)
                
        if unlink and unlink_db:
            self.write(cr, uid, unlink_db.value(), {
                'active': False,
                }, context=context)
                
        return True
        
    _columns = {
        'active': fields.boolean('Active', readonly=True),
        'file_create': fields.datetime('Create date', readonly=True),
        'file_modify': fields.datetime('Modify date', readonly=True),
        'name': fields.char(
            'Name', size=80, required=True, readonly=True),
        'partner_name': fields.char('Partner name', size=80, 
            readonly=True),
        'agent_name': fields.char('Agent name', size=80, 
            readonly=True),
        'fullname': fields.char(
            'Fullname', size=280, required=False, readonly=True),
        'content': fields.text('Content', readonly=True),
        }
        
    _defaults = {
        'active': lambda *x: True,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
