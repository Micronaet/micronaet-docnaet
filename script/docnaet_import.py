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
import pickle
import shutil

pickle_file = './log.p'
try:
    log_db = pickle.load(open(pickle_file, 'rb'))
except:
    print('Log file not present, will be created: %s' % pickle_file)
    log_db = {}    

# Utility:
def xldate_to_datetime(xldatetime): 
    """ Convert float, something like 43705.6158241088, to text date
    """
    import math
    import datetime

    start_date = datetime.datetime(1899, 12, 31)
    (days, portion) = math.modf(xldatetime)

    delta_days = datetime.timedelta(days=days - 1)
    #changing the variable name in the edit
    secs = int(24 * 60 * 60 * portion)
    delta_seconds = datetime.timedelta(seconds=secs)
    result = (start_date + delta_days + delta_seconds)
    return result.strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
sheet_exclude = []
# From config file:
cfg_file = os.path.expanduser('./openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')

# ODOO Docnaet reference:
odoo_path = config.get('odoo', 'path')

protocol_id = 2
language_id = 1
program_id = 11 # TODO get from extension?
company_id = 1
user_id = 30 # Gloria

code_cell = 2
sheet_cell = 3

path = config.get('server', 'path')
selected_files = eval(config.get('server', 'files'))

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
SUPERUSER_ID = 1
document_pool = odoo.model('docnaet.document')
partner_pool = odoo.model('res.partner')
mail_pool = odoo.model('mail.message')
subtype_pool = odoo.model('mail.message.subtype')
user_pool = odoo.model('res.users')

def send_message(subject, body):
    """ Sends message to user_ids
    """
    discussion_ids = subtype_pool.search([
        ('name', '=', 'Discussions'),
        ]) 
    discussion = subtype_pool.browse(discussion_ids)[0]
    users = [user_pool.browse(SUPERUSER_ID)]
    mail_pool.create(values=dict(
            type='email',
            subtype_id=discussion.id,
            partner_ids=[(4, u.partner_id.id) for u in users],
            subject=subject,
            body=body,
            ))
            
log_operation = ''
for root, folders, files in os.walk(path):
    for f in files:
        log_file = ''
        if f.split('.')[-1] not in ('xls', 'xlsx'):
            # log_operation += 'File non Excel: %s\n' % f
            continue
        
        if f not in selected_files:
            # log_operation += 'File non nella selezione: %s' % f
            continue

        xls_file = os.path.join(path, f)        
        if xls_file not in log_db:
            log_db[xls_file] = {}
        wb = xlrd.open_workbook(xls_file)
        sheet_index = {}
        for ws_name in wb.sheet_names():
            ws = wb.sheet_by_name(ws_name)
            if ws_name == 'INDICE':     
                for row in range(ws.nrows):
                    if not row:
                        continue # Jump first line

                    partner_code = ws.cell(row, code_cell).value.strip()
                    sheet_code = ws.cell(row, sheet_cell).value.strip()
                    if not sheet_code:
                        log_file += 'No codice foglio riga: %s' % (row + 1)
                        continue
                        
                    if not partner_code:
                        log_file += 'No codice fornitore riga: %s' % (row + 1)
                        continue
                        
                    if not(partner_code[:2].isdigit() and \
                            partner_code[3:].isdigit() and \
                            partner_code[2:3] == '.'):
                        log_file += 'Codce fornitore formato errato: %s' % \
                            partner_code
                        continue
                    partner_ids = partner_pool.search([
                        ('sql_supplier_code', '=', partner_code)])    

                    if not partner_ids:
                        log_file += 'No codice partner in ODOO: %s' % \
                            partner_code
                        continue

                    if len(partner_ids) > 1:
                        log_file += 'Troppi partner in ODOO: %s' % partner_code
                        continue

                    sheet_index[sheet_code] = partner_ids[0]                  
                continue # Next sheet
            
            if ws_name not in sheet_index:
                log_file += 'Foglio non in indice: %s' % ws_name
                continue
            partner_id = sheet_index[ws_name]
            if ws_name not in log_db[xls_file]:
                log_db[xls_file][ws_name] = {}
                   
            for position in ws.hyperlink_map:
                row, col = position
                try:
                    cell = ws.cell(row, col)
                except:
                    log_file += 'Cella non trovata %s, [%s:%s]' % (
                        ws_name, row, col)
                    continue
                
                link = ws.hyperlink_map[position]
                if link.type != 'url':
                    continue

                product_name = ws.cell(row, 0).value
                supplier_code = ws.cell(row, 1).value
                
                try:
                    request_date = xldate_to_datetime(ws.cell(row, 2).value)
                except:
                    request_date = ''
                date_value = xldate_to_datetime(cell.value)

                name = product_name
                description = 'Fornitore %s, Richiesta %s, Aggiornata %s' % (
                    ws_name,
                    request_date[:10],
                    date_value[:10],
                    )
                note = 'Importato da file %s' % xls_file
                        
                file_link = os.path.join(path, link.url_or_path)
                
                if file_link not in log_db[xls_file][ws_name]:
                    log_db[xls_file][ws_name][file_link] = False # Docnaet ID
                    
                docnaet_extension = file_link.split('.')[-1].lower()

                odoo_data = {
                    'name': name,
                    'supplier_code': supplier_code,                    
                    'protocol_id': protocol_id,
                    'description': description,
                    'note': note,
                    'number': False,
                    'date': date_value,
                    'language_id': language_id,
                    'type_id': False,
                    'company_id': company_id,
                    'user_id': user_id,
                    'partner_id': partner_id,
                    'docnaet_partner_ids': [(6, 0, [partner_id])],
                    'product_id': False,
                    'docnaet_product_ids': False,
                    'docnaet_extension': docnaet_extension,
                    'docnaet_mode': 'docnaet',
                    'imported': True,
                    'program_id': program_id,
                    #'priority': 'normal',
                    #'state': 'draft',
                    }
                
                if log_db[xls_file][ws_name][file_link]: # Update
                    document_pool.write(
                        log_db[xls_file][ws_name][file_link], odoo_data)
                else:
                    log_db[xls_file][ws_name][file_link] = \
                        document_pool.create(odoo_data).id
                    pickle.dump(log_db, open(pickle_file, 'wb')) # History

                # -------------------------------------------------------------                    
                # File operations:    
                # -------------------------------------------------------------                    
                odoo_id = log_db[xls_file][ws_name][file_link]
                odoo_file = os.path.join(
                    odoo_path, '%s.%s' % (odoo_id, docnaet_extension))


                if os.path.isfile(odoo_file):
                    log_file += 'File presente in ODOO %s\n' % odoo_file
                else:
                    log_file += 'Copying %s ODOO file\n' % odoo_file
                    shutil.copy(file_link, odoo_file)
        send_message('File: %s' % f, log_file.replace('\n', '<br/>'))

send_message('Log importazione completa', log_operation.replace('\n', '<br/>'))
