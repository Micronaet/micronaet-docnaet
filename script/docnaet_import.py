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
import erppeek
import xlrd
import ConfigParser

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# From config file:
cfg_file = os.path.expanduser('../openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

path = os.path.expanduser(config.get('server', 'path'))

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

# Pool used:
import pdb; pdb.set_trace()
document_pool = odoo.model('docnaet.document')
for root, folders, files in os.walk(path):
    for f in files:
        if f.split('.')[-1] not in ('xls', 'xlsx'):
            print 'File not used: %s' % f
            continue
        else:
            print 'File used: %s' % f
            
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

