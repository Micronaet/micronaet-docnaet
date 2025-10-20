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
import shutil
import pickle
import pdb

try:
    import ConfigParser
except:
    import configparser as ConfigParser


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
file_account = config.get('input', 'account')  # File used as whoami check file!

protocol_id = int(config.get('default', 'protocol_id'))
program_id = int(config.get('default', 'program_id'))
user_id = int(config.get('default', 'user_id'))
docnaet_category_id = int(config.get('default', 'docnaet_category_id'))
company_id = int(config.get('default', 'company_id'))
language_id = int(config.get('default', 'language_id'))

default_data = {
    'docnaet_category_id': docnaet_category_id,
    'company_id': company_id,
    'protocol_id': protocol_id,
    'language_id': language_id,
    'user_id': user_id,
    'program_id': program_id,
    'docnaet_extension': 'pdf',
    'docnaet_mode': 'docnaet',
    'priority': 'normal',
    'note': 'Importazione automatica'
}

# ----------------------------------------------------------------------------------------------------------------------
#                                                 Utility:
# ----------------------------------------------------------------------------------------------------------------------
def get_name(invoice_ref, date):
    """ Return invoice name if correct format:
        from "FT01.000336" to "8/xxx del 05.05.25"
    """
    return '{}/{} del {}.{}.{}'.format(
        int(invoice_ref[2:4]),
        int(invoice_ref[5:]),

        date[8:10],
        date[5:7],
        date[2:4],
    )

# ----------------------------------------------------------------------------------------------------------------------
# Mount check:
# ----------------------------------------------------------------------------------------------------------------------
# Account File used for this check:
if not os.path.isfile(file_account):
    print('File contabile non presente {} (o server non collegato), non viene importato nulla!'.format(file_account))
    sys.exit()

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
excluded_code = ['270', '290']
exclude_invoice = {
    '2025': {
        '201': 622,
        '230': 294,
    },
}

print('Lettura file contabile {}'.format(file_account))
account_db = {}
with open(file_account, 'r') as file_csv:
    counter = 0
    for line in file_csv:
        counter += 1
        try:
            year, invoice_ref, date, customer_code = line.strip().split('|')
            if year not in account_db:
                account_db[year] = {}
            account_db[year][invoice_ref] = [date, customer_code]
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
# Note: both path need to be on ODOO Server where Docnaet is installed!

years = [from_year, ]  # todo from to this
try:
    for this_year in years:
        this_path = folder_mask.format(year=this_year)
        if this_path not in file_db:
            file_db[this_path] = {}

        for root, folders, files in os.walk(this_path):
            # ----------------------------------------------------------------------------------------------------------
            #                                                Invoice file:
            # ----------------------------------------------------------------------------------------------------------

            for filename in files:
                fullname = os.path.join(root, filename)
                invoice_ref = filename.split('_')[0]  # todo check  	"FT01.000336"
                if invoice_ref not in account_db.get(this_year, {}):
                    print('File non identificabile da gestionale {}, saltato'.format(filename))
                    continue

                # ------------------------------------------------------------------------------------------------------
                #                                         ODOO Docnaet record:
                # ------------------------------------------------------------------------------------------------------
                date, customer_code = account_db[this_year][invoice_ref]
                auto_import_key = 'INVOICE-{}.{}'.format(year, invoice_ref)  # Key
                invoice_number = int(invoice_ref.split('.')[-1])
                customer_mode = customer_code[:3]
                from_number = exclude_invoice[this_year].get(customer_mode, 0)
                if invoice_number < from_number:
                    print('Codice partner {} e fattura {}, sotto la soglia {}, non importata'.format(
                        customer_mode, invoice_ref, from_number))
                    continue

                # Read ODOO record:
                doc_ids = doc_pool.search([
                    ('auto_import_key', '=', auto_import_key),
                ])
                if doc_ids:
                    doc_id = doc_ids[0]
                    document = doc_pool.browse(doc_id)
                    print('Select {}'.format(invoice_ref))

                else:
                    # --------------------------------------------------------------------------------------------------
                    #                                          Search partner:
                    # --------------------------------------------------------------------------------------------------
                    partner_ids = partner_pool.search([
                        ('sql_customer_code', '=', customer_code),
                    ])

                    # --------------------------------------------------------------------------------------------------
                    # Exclude clause:
                    # --------------------------------------------------------------------------------------------------
                    # Not found:
                    if not partner_ids:
                        print('Codice partner {} non trovato, non importato {}'.format(customer_code, invoice_ref))
                        continue
                    partner_id = partner_ids[0]
                    partner = partner_pool.browse(partner_id)
                    customer_name = partner.name or ''

                    # Customer code not used:
                    if customer_code[:3] in excluded_code:
                        print('Partner escluso {}, non importata {}'.format(
                            customer_code, customer_name, invoice_ref))
                        continue

                    # Customer name "Cliente":
                    if customer_name.startswith('Cliente'):
                        print('Partner non riconosciuto {}, non importato {}'.format(
                            customer_code, customer_name, invoice_ref))
                        continue

                    # Invoice not present in ODOO create:
                    record = default_data.copy()
                    # todo format date?

                    # Create if not present (create record with default values)
                    if partner.country_id:
                        country_id = partner.country_id.id
                    else:
                        country_id = partner.company_id.country_id.id
                        
                    record.update({
                        'name': get_name(invoice_ref, date), # '{} del {}'.format(invoice_ref, date),
                        # 'number': '',
                        'date': date,
                        'partner_id': partner_id,
                        'country_id': country_id,

                        'auto_import_key': auto_import_key,
                    })
                    document = doc_pool.create(record)
                    doc_id = document.id
                    print('Create {}'.format(invoice_ref))

                # ------------------------------------------------------------------------------------------------------
                # Check document state for WF confirm:
                # ------------------------------------------------------------------------------------------------------
                if document.state == 'draft':
                    # Confirm document (assign number protocol)
                    odoo.exec_workflow('docnaet.document', 'document_draft_confirmed', doc_id)

                # ------------------------------------------------------------------------------------------------------
                # Check if need to be updated the file:
                # ------------------------------------------------------------------------------------------------------
                # Get filename in ERP
                this_filename = doc_pool.erppeek_get_document_filename(doc_id)
                modify_ts = os.path.getmtime(fullname)
                update_file = False
                if not os.path.isfile(this_filename):  # destination
                    update_file = True
                else:
                    stored_modify_ts = file_db.get(this_path, {}).get(fullname)
                    if modify_ts != stored_modify_ts:  # File original modified:
                        file_db[this_path][fullname] = modify_ts
                        update_file = True

                if update_file:
                    # shutil.copy(fullname, this_filename)
                    print(' > ***** Update file {}'.format(fullname))
                else:
                    print(' > No need to update, file {}'.format(fullname))
            break   # Only base subfolder

    # Save Pickle:
finally:
    print('Result: {}'.format(sys.exc_info()))
    try:
        with open(file_pickle, 'wb') as file:
            pickle.dump(file_db, file)
        print('Storicizzato file pickle {}'.format(file_pickle))
    except:
        print('Errore salvataggio file pickle {}, viene rigenerato la prossima volta!'.format(file_pickle))