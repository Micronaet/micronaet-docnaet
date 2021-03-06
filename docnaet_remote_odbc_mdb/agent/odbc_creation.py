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
# Launch python ./odbc_creation new # For create new database from empty
# Launch python ./odbc_creation update # For update database from current

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
docnaet_mode = 'docnaet' # TODO parametrize in config file

# Access:
path_database = config.get('mdb', 'path')
mdb_start = config.get('mdb', 'start') #'start.docnaet.mdb'
mdb_execute = config.get('mdb', 'execute') #'execute.docnaet.mdb'
mdb_agent = config.get('mdb', 'agent') #'docnaet.mdb'

# Launch parameter:
try:
    mode = sys.argv[1] # update, new
except:
    mode = 'new'
    
try:
    update_period = int(sys.argv[2]) # days
except:
    mode = 10 

# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
def mo(field):
    ''' Clean many2one fields
    '''
    if field:
        return field.id
    else:
        return False

def s(value):
    ''' Remove not ascii char
    '''    
    if not value:
        return ''
    value = '%s' % value
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
if mode == 'update':
    mdb['start'] = mdb_agent # use previous generated (not empty)
    
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
verbose = False # TODO True log query export
import_table = [
    'Lingue',
    'Tipologie',
    'Protocolli',
    'Tipi',
    'Nazioni',
    'Utenti',
    'Clienti',
    'Documenti',
    ]
    
priority_db = { # not used for now
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
        ('record.id', 's(record.name)', 's(record.note)'), # OpenERP fields
        ('ID_lingua', 'linDescrizione', 'linNote'), # MDB fields (same order)
        ],

    'Tipologie': [
        'DocnaetType',
        [],
        ('record.id', 's(record.name)', 's(record.note)'),
        ('ID_tipologia', 'tipDescrizione', 'tipNote'),
        ],
        
    'Protocolli': [
        'DocnaetProtocol',
        [],
        ('record.id', 's(record.name)', 's(record.note)'),
        ('ID_protocollo', 'proDescrizione', 'proNote'),
        ],
        
    'Tipi': [
        'ResPartnerDocnaet',
        [],
        ('record.id', 's(record.name)', 's(record.note)'),
        ('ID_tipo', 'tipDescrizione', 'tipNote'),
        ],
        
    'Nazioni': [
        'ResCountry',
        [],
        ('record.id', 's(record.name)'),
        ('ID_nazione', 'nazDescrizione'),
        ],

    'Utenti': [
        'ResUsers',
        [],
        (
            'record.id', 's(record.login)', 's(record.password)', 
            '10', 's(record.name)',
            '-1', '-1', 
            's(\'111\')', '-1', 
            ),
        (
            'ID_utente', 'uteUserName', 'utePassword', 
            'uteLivello', 'uteDescrizione', 
            'uteNonEliminabile', 'uteAdministrator', 
            'uteConfigurazione', 'uteGestore',
            ),
        ],
                
    'Clienti': [
        'ResPartner',
        [('docnaet_enable','=', True)],
        (
            'record.id', 's(record.name)', 's(record.street)', 
            'mo(record.country_id)', 'mo(record.docnaet_category_id)',
            ),
        (
            'ID_cliente', 'cliRagioneSociale', 'cliIndirizzo', 
            'ID_nazione', 'ID_tipo',
            ),
        ],
        
    'Documenti': [
        'DocnaetDocument',
        [('docnaet_mode', '=', docnaet_mode)], # Docnaet / Labnaet mode
        (
            'record.id', 'mo(record.protocol_id)', 'mo(record.partner_id)', 
            'mo(record.language_id)', 'mo(record.user_id)', 
            's(record.name)', 's(record.description)', 's(record.note)',
            'record.number', 'record.fax_number', 
            's(record.docnaet_extension)', 's(record.date)', 
            's(record.real_file)', 'mo(record.type_id)',
            #'priority_db.get(record.priority, 3)'
            ),
        (
            'ID_documento', 'ID_protocollo', 'ID_cliente', 
            'ID_lingua', 'ID_utente', 
            'docOggetto', 'docDescrizione', 'docNote',
            'docNumero', 'docFax', 
            'docEstensione', 'docData', 
            'docFile', 'ID_tipologia',
            #'ID_'
            ),
        ],
    }

if mode == 'update':
    last_update = datetime.now() - timedelta(days=update_period)
    
    # Modify domain for DocnaetDocument:
    convert_db['Documenti'][1] = [
        ('write_date', '>=', last_update.strftime('%Y-%m-%d')),
        ]
    
    # Clean anagrafic tables not Documenti:
    for table in import_table:
        if table == 'Documenti':
            continue
            
        # Remove document if update:        
        query = 'DELETE FROM %s;' % table
        if verbose:
            print '[INFO] %s. Delete query: %s' % (i, query)
        try:    
            cr.execute(query)
            cr.commit()
        except:
            print '[ERROR] %s remove items: %s' % (
                table, sys.exc_info(), 
                )
                
for table in import_table:
    item = convert_db[table]
        
    obj, domain, oerp_fields, mdb_fields = item    
    fields = ('%s' % (mdb_fields, )).replace('\'', '')
    erp_pool = eval('erp.%s' % obj) # Connect with Oerp Obj    
    
    # Loop on all record:
    erp_ids = erp_pool.search(domain)
    i = 0
    
    # Delete previous documents if update period
    if mode == 'update' and table == 'Documenti':
        print '[INFO] Delete document of update period: [record: %s]' % (
            len(erp_ids), 
            )
        query = 'DELETE FROM %s WHERE id in %s;' % (
            table, erp_ids,
            )
        
    print '[INFO] Start export %s [record: %s]' % (
        table, len(erp_ids))        
    for record in erp_pool.browse(erp_ids):
        i += 1
        if i % 100 == 0:
            print '[INFO] ... %s record exported: %s' % (table, i)
            
        values = tuple([eval(v) for v in oerp_fields])
        query = 'INSERT INTO %s %s VALUES %s' % (
            table,
            fields,            
            values,
            )
        if verbose:
            print '[INFO] %s. Query: %s' % (i, query)
        try:    
            cr.execute(query)
            cr.commit()
        except:
            print '[ERROR] %s export: %s' % (
                table, sys.exc_info(), 
                )
                
if 'Documenti' in import_table:
    # Change for problem:
    query = '''
        UPDATE Documenti SET docFile = '' WHERE docFile = '0';
        '''
    cr.execute(query)
    cr.commit()
    print '[INFO] docFile null when 0'

# close the cursor and connection
cr.close()
connection.close()
# Final rename for agent copy:
shutil.move(mdb['execute'], mdb['agent'])
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
