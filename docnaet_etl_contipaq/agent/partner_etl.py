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
import pyodbc
import erppeek
import ConfigParser

# -----------------------------------------------------------------------------
#                                UTILITY
# -----------------------------------------------------------------------------
def get_erp(URL, database, user, password):
    ''' Connect to log table in ODOO
    '''
    return erppeek.Client(
        URL,
        db=database,
        user=user,
        password=password,
        )   

# -----------------------------------------------------------------------------
#                                Parameters
# -----------------------------------------------------------------------------
# Extract config file name from current name
path, name = os.path.split(os.path.abspath(__file__))
fullname = os.path.join(path, 'openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([fullname])

# DSN block:
dsn = config.get('dsn', 'name') 
uid = config.get('dsn', 'uid') 
pwd = config.get('dsn', 'pwd') 

# OpenERP block:
hostname = config.get('openerp', 'server')
port = config.get('openerp', 'port')
database = config.get('openerp', 'database')
user = config.get('openerp', 'user')
password = config.get('openerp', 'password')

URL = 'http://%s:%s' % (hostname, port) 

# Access MS SQL Database customer table:
connection = pyodbc.connect('DSN=%s;UID=%s;PWD=%s' % (dsn, uid, pwd))
cr = connection.cursor()

query = '''
    SELECT 
        CIDCLIENTEPROVEEDOR, CCODIGOCLIENTE, CRAZONSOCIAL, CFECHAALTA, 
        CRFC, CDENCOMERCIAL, CTIMESTAMP, CEMAIL1, CEMAIL2, CEMAIL3, 
        CTIPOENTRE
    FROM dbo.admClientes
    WHERE 
        CIDCLIENTEPROVEEDOR > 0;
    ''' #CCODIGOCLIENTE ilike 'PR%' AND 
try:
    cr.execute(query)
except:
    print 'Error: %s' % (sys.exc_info(), )

# OPENERP Obj: 
erp = get_erp(URL, database, user, password)

# Read category:
category_pool = erp.ResPartnerDocnaet
category_ids = category_pool.search([('account_start_code', '!=', False)])
category_db = {}
for category in category_pool.browse(category_ids):
    category_db[category.account_start_code] = (
        category.id, category.customer, category.supplier)

# Read partner:
partner_pool = erp.ResPartner
for row in cr.fetchall():
    item_id = row[0]
    ref = row[1]
    name = row[2]
    vat = row[4]
    email = row[7]
    email1 = row[8]
    email2 = row[9]

    data = {
        'is_company': True,
        'docnaet_enable': True, # default
        'ref': ref,
        'name': name,
        #'vat': vat,
        'email': email,
        #email1
        #email2
        }
    
    for start, record in category_db.iteritems():
        (category_id, customer, supplier) = record
        if ref.startswith(start):
            data['docnaet_category_id'] = category_id
            if customer:
                data['customer'] = True
            if supplier:
                data['supplier'] = True
    partner_ids = partner_pool.search([('ref', '=', ref)])
    if partner_ids:
        partner_pool.write(partner_ids, data)
        print 'Update: %s' % name
    else:
        partner_pool.create(data)
        print 'Insert: %s' % name
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
