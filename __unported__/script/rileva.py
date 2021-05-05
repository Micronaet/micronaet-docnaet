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
import xlsxwriter
import ConfigParser

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# Excel file: 
file_out = './carichi_di_produzione.xlsx'

# From config file:
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
load_pool = odoo.model('mrp.production.workcenter.line')	

# Excel:
WB = xlsxwriter.Workbook(file_out)
WS = WB.add_worksheet('Carichi')

# Header
row = 0
WS.write(row, 0, 'Codice')
WS.write(row, 1, 'Prodotto')
WS.write(row, 2, 'Produzione')
WS.write(row, 3, 'Data')
WS.write(row, 4, 'Q.')
WS.write(row, 5, 'Costo')
WS.write(row, 6, 'Dettaglio')

load_ids = load_pool.search([
    ('product_price_calc', '!=', False),
    ])
    
total = len(load_ids)
loads = sorted(
    load_pool.browse(load_ids), 
    key=lambda x: (x.product.default_code, x.start_date))
    
for load in loads:
    row += 1
    if not row % 10:
        print('Write %s of %s' % (row, total))
    product = load.product
    detail = load.product_price_calc
    medium = detail.split('<b>')[-1][:-4]

    # Data
    WS.write(row, 0, product.default_code)
    WS.write(row, 1, product.name)
    WS.write(row, 2, load.production_id.name)
    WS.write(row, 3, load.date_start)
    WS.write(row, 4, load.qty)
    WS.write(row, 5, medium)
    WS.write(row, 6, detail.replace('<br>', '\n').replace(
        '<br/>', '\n').replace(
            '<b>', '').replace(
                '</b>', ''))
    
try:
    WB.close()
except:
    print('Errore chiudendo file XLSX')

