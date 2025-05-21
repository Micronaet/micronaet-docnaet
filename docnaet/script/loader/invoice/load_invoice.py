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
import pickle

from docnaet_remote_odbc_mdb.agent.odbc_creation import path_database

# ======================================================================================================================
# Read configuration parameter:
# ======================================================================================================================
cfg_file = os.path.expanduser('../openerp.cfg')

# ERP parameter:
config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

# Input parameter:
folder_mask = config.get('input', 'folder')
from_year = config.get('input', 'year')
file_pickle = config.get('input', 'pickle')
file_account = config.get('input', 'account')

# ----------------------------------------------------------------------------------------------------------------------
# Connect to ODOO:
# ----------------------------------------------------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=pwd,
    )
doc_pool = odoo.model('docnaet.document')
partner_pool = odoo.model('res.partner')

# ======================================================================================================================
# Load files from Path:
# ======================================================================================================================
# Account File:
if not os.path.isfile(file_account):
    print('File contabile non presente {}, non importo!'.format(file_account))
    sys.exit()

print('Lettura file contabile {}'.format(file_account))
account_db = {}
with open(file_account, 'r') as file_csv:
    counter = 0
    for line in file_csv:
        counter += 1
        try:
            year, invoice, date, customer_code = line.split('|')
            if year not in account_db:
                account_db[year] = {}
            account_db[year] = [invoice, date, customer_code]
        except:
            print('{}. Riga saltata'.format(file_account))
            continue

# Load Pickle:
try:
    with open(file_pickle, 'rb') as file:
        file_db = pickle.load(file)
        print('Caricato file pickle {}'.format(file_pickle))
except Exception as e:
    print('File pickle {} non presente, creato un database vuoto'.format(file_pickle))
    file_db = {}

# Read folders:
years = [year]  # todo from to this
for this_year in years:
    this_path = path_database.format(year=this_year)
    if this_path not in file_db:
        file_db[this_path] = []
    for root, folders, files in os.path.walk(this_path):
        for filename in files:
            fullname = os.path(root, filename)
            invoice_ref = filename.split('_')[0]  # todo check
            if invoice_ref not in account_db:
                print('File non identificabile da gestionale {}, saltato'.format(filename))
                continue
            invoice_detail = account_db[invoice_ref]

            # Read ODOO record:

            # Create if not present (create record with default values)

            # Check if need to be updated the file

            # Get filename in ERP

            # Save filename timestamp in picked db


# -----------------------------------------------------------------------------
doc_ids = doc_pool.search([
    ('date_month', '=', False),
])

# Save Pickle:
try:
    with open(file_pickle, 'wb') as file:
        pickle.dump(file_db, file)
    print('Storicizzato file pickle {}'.format(file_pickle))
except Exception as e:
    print('Errore salvataggio file pickle {}, viene rigenerato la prossima volta!'.format(file_pickle))