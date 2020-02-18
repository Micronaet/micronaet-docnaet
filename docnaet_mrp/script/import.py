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
import time
import pytz
from datetime import datetime

# ----------------
# Read parameters:
# ----------------
config = ConfigParser.ConfigParser()
config.read(['./config.cfg'])

server = config.get('OpenERP', 'server')
port = config.get('OpenERP', 'port')
dbname = config.get('OpenERP', 'dbname')
user = config.get('OpenERP', 'user')
password = config.get('OpenERP', 'pwd')

filesystem_path = os.path.expanduser(config.get('path', 'filesystem'))
docnaet_path = os.path.expanduser(config.get('path', 'docnaet'))

def get_create_date(fullname):
    """ Extract create date from file:
    """
    t = os.stat(fullname).st_ctime
    t = time.localtime(t)
    formatted = time.strftime('%Y-%m-%d %H:%M:%S', t)
    tz = str.format('{0:+06.2f}', float(time.timezone) / 3600)
    final = formatted + tz
    return final[:19]

# --------------
# Client erpeek:
# --------------
erp = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=password,
    )
print 'Connecting ODOO %s: %s:%s' % (dbname, server, port)    

# Pool used:
mrp_pool = erp.MrpProduction
docnaet_pool = erp.DocnaetDocument


# Fixed parameter (setup before):
file_extension = 'pdf'

company_id = 1
partner_id = 1
user_id = 1
priority_id = 3
protocol_id = 78
language_id = 1 
type_id = False

# TODO Attenzione ai documenti puntatori (doppio ciclo per assegnazione parent)
print 'Read filesystem: %s' % filesystem_path)
import pdb; pdb.set_trace()

for root, folders, files in os.walk(filesystem_path):
    for folder in folders:
        date_folder = os.path.join(root, folder)
        date = '%s-%s-01' % (folder[:4], folder[4:6])
        for date_root, date_folders, date_files in os.walk(date_folder):                
            for filename in date_files:
                name_part = filename.split('.')

                mrp_name = name_part[0]
                extension = name_part[-1]

                if extension.lower() != file_extension:
                    print 'Jump no PDF: %s' % filename
                
                fullname = os.path.join(date_root, filename)

                # Fields:
                create_date = get_create_date(fullname)
                name = 'Foglio di produzione %s' % mrp_name
                description = 'Scansione foglio di produzione %s [%s]' % (
                    mrp_name,
                    create_date,
                    )
                note = 'Importato con procedure automatica [%s]' % \
                    datetime.now()
                
                # -------------------------------------------------------------
                # Search production:
                # -------------------------------------------------------------
                mrp_ids = mrp_pool.search([
                    ('name', '=', mrp_name),
                    ])
                if mrp_ids:
                    linked_mrp_id = mrp_ids[0]
                else:
                    print 'MRP %s not found!' % mrp_name
                    linked_mrp_id = False
                     
                # -------------------------------------------------------------
                # Create document:
                # -------------------------------------------------------------
                #date_create
                #extension = file_extension
                #protocol_id
                #language_id 
                #type_id 
                
                # Create / Update operations:
                data = {        
                    'company_id': company_id,
                    'partner_id': partner_id,
                    'user_id': user_id,
                    'protocol_id': protocol_id,
                    'language_id': language_id,
                    'type_id': type_id,
                    'date': date,
                    #'create_date': create_date,
                    'name': name,
                    'description': description,
                    'note': note,
                    #'number': number,
                    'docnaet_extension': file_extension,
                    }

                document_ids = docnaet_pool.search([
                    ('name', '=', name),
                    ])
                if document_ids:
                    # Update
                    docnaet_pool.write(document_ids, data)
                    print 'Update record %s' % mrp_name
                    docnaet_id = document_ids[0]
                    # continue # File yet present!?!
                else:
                    # Create
                    docnaet_id = docnaet_pool.create(data).id
                    print 'Create record %s' % mrp_name
                docnaet_fullname = os.path.join(docnaet_path, '%s.%s' % (
                    docnaet_id, file_extension))
                print '   Import file: %s > %s' % (fullname, docnaet_fullname)

