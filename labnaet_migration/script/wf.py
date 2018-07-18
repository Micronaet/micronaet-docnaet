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
import csv
import erppeek
import ConfigParser

# -----------------------------------------------------------------------------
# Read parameters:
# -----------------------------------------------------------------------------
config = ConfigParser.ConfigParser()
config.read(['config.cfg'])

server = config.get('OpenERP', 'server')
port = config.get('OpenERP', 'port')
dbname = config.get('OpenERP', 'dbname')
user = config.get('OpenERP', 'user')
password = config.get('OpenERP', 'password')

# -----------------------------------------------------------------------------
# Client ODOO:
# -----------------------------------------------------------------------------
erp = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=password,
    )

document_pool = erp.DocnaetDocument
document_ids = document_pool.search([('state', '=', 'draft')])
i = 0
for item_id in document_ids: 
    i += 1
    print i 
    #erp.execute_kw(
    import pdb; pdb.set_trace()
    erp.exec_workflow(
        'docnaet.document', 
        'document_draft_confirmed', 
        item_id)

