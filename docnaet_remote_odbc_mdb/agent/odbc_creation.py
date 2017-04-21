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
# Utility:
# -----------------------------------------------------------------------------
def clean_ascii(value):
    ''' Remove not ascii char
    '''    
    if type(value) not in (unicode, str):
        return value
    
    if not value:
        return ''

    res = ''
    for c in value:
        if ord(c) <= 127:
              res += c
    res = res.replace('\'', ' ')          
    return str(res)

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
erp = erppeek.Client(
    'http://%s:%s' % (host, port),
    db=database,
    user=username,
    password=password,
    )

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
except:
    print '[ERROR] Connection to database %s\nString: %s\n[%s]' % (
        mdb['execute'],
        odbc_string,
        sys.exc_info(),
        )
    sys.exit()    

# Create cursor:
cr = connection.cursor()

# Populate database:
priority_db = {
    'lowest': 1,
    'low': 2, 
    'normal': 3,
    'high': 4,
    'highest': 5,
    }

convert_db = {
    'Lingue': [
        'DocnaetLanguage', # OpenERP Object for Erppeek
        [], # OpenERP domain filter
        ('record.id', 'record.name', 'record.note'), # OpenERP fields
        ('ID_lingua', 'linDescrizione', 'linNote'), # MDB fields (same order)
        ],

    'Tipologie': [
        'DocnaetType',
        [],
        ('record.id', 'record.name', 'record.note'),
        ('ID_tipologia', 'tipDescrizione', 'tipNote'),
        ],
        
    'Protocolli': [
        'DocnaetProtocol',
        [],
        ('record.id', 'record.name', 'record.note'),
        ('ID_protocollo', 'proDescrizione', 'proNote'),
        ],
        
    'Tipi': [
        'ResPartnerDocnaet',
        [],
        ('record.id', 'record.name', 'record.note'),
        ('ID_tipo', 'tipDescrizione', 'tipNote'),
        ],
        
    'Nazioni': [
        'ResCountry',
        [],
        ('record.id', 'record.name'),
        ('ID_nazione', 'nazDescrizione'),
        ],
        
    'Clienti': [
        'ResPartner',
        [('docnaet_enable','=', True)],
        ('record.id', 'record.name', 'record.street'),
        ('ID_cliente', 'cliRagioneSociale', 'cliIndirizzo'),
        ],
        
    'Documenti': [
        'DocnaetDocument',
        [],
        (
            'record.id', 'record.protocol_id.id', 'record.partner_id.id', 
            'record.name', 'record.description', 'record.note', 
            'record.number', 
            ),
        (
            'ID_documento', 'ID_protocollo', 'ID_cliente', 
            'docOggetto', 'docDescrizione', 'docNote', 
            'docNumero', 
            ),
        ],
              
    #TODO (fare dopo, è diventata una selection)
#    'Importanza': [
#        'docnaet.import
#        ('ID_importanza', 'impDescrizione'), # MDB Fields:
#        ]
    }
for table, item in convert_db.iteritems():
    obj, domain, oerp_fields, mdb_fields = item    

    fields = ('%s' % (mdb_fields, )).replace('\'', '')
    erp_pool = eval('erp.%s' % obj) # Connect with Oerp Obj    
    
    # Loop on all record:
    erp_ids = erp_pool.search(domain)
    for record in erp_pool.browse(erp_ids):
        values = tuple([clean_ascii(eval(v)) for v in oerp_fields])
        query = 'INSERT INTO %s %s VALUES %s' % (
            table,
            fields,            
            values,
            )
        print '[INFO] Query: %s' % query
        try:    
            cr.execute(query)
            cr.commit()
        except:
            print '[ERROR] Error: %s' % (sys.exc_info(), )

# close the cursor and connection
cr.close()
connection.close()

# Final rename for agent copy:
shutil.move(mdb['execute'], mdb['agent'])
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
