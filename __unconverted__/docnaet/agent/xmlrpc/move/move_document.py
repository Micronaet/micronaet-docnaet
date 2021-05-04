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
import erppeek
import ConfigParser
import shutil

# Parameters:
protocol_id = 78

from_path = os.path.expanduser('~/filestore/docnaet/1/store')
to_path = os.path.expanduser('~/filestore/labnaet/1/store')
    
# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('../openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (
        server, port), 
    db=dbname,
    user=user,
    password=pwd,
    )
print 'Connect with ODOO: %s' % odoo    

# -----------------------------------------------------------------------------
# Extract product uom:
# -----------------------------------------------------------------------------
document_pool = odoo.model('docnaet.document')
document_ids = document_pool.search([
    ('protocol_id', '=', protocol_id),
    ])

# TODO protocol nedd to be manually moved in docnaet_mode labnaet:
"""
for doc in document_pool.browse(document_ids):
    labnaet_id = document_pool.get_counter_labnaet_id()
    docnaet_id = doc.id
        
    # move file:
    from_file = os.path.join(
        from_path, 
        '%s.%s' % (docnaet_id, doc.docnaet_extension),
        )
    to_file =  os.path.join(
        to_path, 
        '%s.%s' % (labnaet_id, doc.docnaet_extension),
        )

    if os.path.isfile(to_file):
        print 'Copy failed, yet present: %s' % to_file        
    else:
        print 'Copy: %s > %s' % (from_file, to_file)
    shutil.copy(from_file, to_file)

    document_pool.write([docnaet_id], {
        'docnaet_mode': 'labnaet',
        'labnaet_id': labnaet_id,
        })
"""        

tot = len(document_ids)
for doc in document_pool.browse(document_ids):
    docnaet_id = doc.id
    from_file = os.path.join(
        from_path, 
        '%s.%s' % (docnaet_id, doc.docnaet_extension),
        )
    try:
        os.remove(from_file)
        print 'Remove: % / %s' % (from_file, tot)
    except: 
        print 'Cannot remove: %s' % from_file    
    
    
    

