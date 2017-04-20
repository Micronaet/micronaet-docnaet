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
import ConfigParser
import erppeek
import pyodbc
import shutil
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# Parameters:
# -----------------------------------------------------------------------------
# Config file (home folder of current user):
cfg_file = os.path.join('.', 'odbc.cfg')
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# ODOO:
host = config.get('openerp', 'host')
port = config.get('openerp', 'port')
database = config.get('openerp', 'database')
username = config.get('openerp', 'username')
password = config.get('openerp', 'password')

# Access:
path_database = config.get('mdb', 'path')
mdb_start = config.get('mdb', 'start') #'start.docnaet.mdb'
mdb_execute = config.get('mdb', 'execute') #'execute.docnaet.mdb'
mdb_agent = config.get('mdb', 'agent') #'docnaet.mdb'

# -----------------------------------------------------------------------------
# Add calculated parameters:
# -----------------------------------------------------------------------------
# Generate fullname:    
path_database = os.path.expanduser(path_database)
mdb = {
    'start': mdb_start,
    'execute': mdb_execute,
    'agent': mdb_agent,
    }
for key, value in mdb.iteritems():
    mdb[key] = os.path.join(path_database, value)

# ODBC string:
odbc_string = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source=%s' % (
    mdb['execute'])

# -----------------------------------------------------------------------------
# Open connection via ERP Peek with ODOO
# -----------------------------------------------------------------------------
# Connect:

# Read data:

# -----------------------------------------------------------------------------
# Migration of data:
# -----------------------------------------------------------------------------
# Copy default access database for start:
shutil.copyfile(mdb['start'], mdb['execute'])

# Connect to the database:
try:
    connection = pyodbc.connect(
        'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s' % mdb['execute'])
    cursor = connection.cursor()
except:
    print '[ERROR] Connection to database %s\nString: %s\n[%s]' % (
        mdb['execute'],
        odbc_string,
        sys.exc_info(),
        )
    sys.exit()    

# Populate database:
table = 'Importanza'

# create a cursor
cr = connection.cursor()

# extract all the data
import pdb; pdb.set_trace()
query = 'INSERT INTO %s %s VALUES %s' % (
    table,
    ('ID_importanza', 'impDescrizione'),
    (1, 'Importante'),
    )
cr.execute(query)
cr.commit()

# close the cursor and connection
cr.close()
connection.close()

# Final rename for agent copy:
shutil.move(mdb['execute'], mdb['agent'])
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
