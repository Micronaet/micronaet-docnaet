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

import sys
import os
import pymssql
import excel_export

# -----------------------------------------------------------------------------
# Parameters:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('./openerp.cfg')
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# SQL:
host = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
password= config.get('dbaccess', 'pwd')
database = config.get('dbaccess', 'server')

# Filesystem:
root_path = config.get('filesystem', 'root')

# -----------------------------------------------------------------------------
# MS SQL:
# -----------------------------------------------------------------------------
connection = pymsql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    as_dict=True,       
)
cr = connection.cursor()

database = {
    'application': {},
    'category': {},
    'partner': {},
    'company': {},
    'important': {},
    'language': {},
    'country': {},
    # 'product': {},
    'protocol': {},
    # 'sent': {},
    # 'support': {},
    'type': {},
    'user': {},
    'document': {},
    }

# -----------------------------------------------------------------------------
# Nazioni:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Nazioni')
for item in cr.fetchall():
    item_id = item['ID_nazione']
    database['country'][item_id] = item  # nazDescrizione, nazNote

# -----------------------------------------------------------------------------
# Document:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Documenti')
for item in cr.fetchall()[:10]:  # TODO remove me
    database['document'].append(item)
    
# -----------------------------------------------------------------------------
# Generate XLSX files:
# -----------------------------------------------------------------------------
ExcelWriter = excel_export.excel_wrapper.ExcelWriter

# Create WB:
WB = ExcelWriter('./data/Docnaet.xlsx', verbose=True)
excel_format = {
    'f_title': WB.get_format('title'),
    'f_header': WB.get_format('header'),
    'f_text': WB.get_format('text'),
    'f_number': WB.get_format('number'),
    'f_text_red': WB.get_format('bg_red'),
    'f_number_red': WB.get_format('bg_red_number'),
    }
    
header = [
    'APRI', 'Colleg.',
    'Azienda', 
    'Protocollo', 'Numero', 'Fax',
    'Data', 'Scadenza',
    'Cliente', 'Categoria', 'Nazione', 
    'Tipologia', 'Lingua', 'Applicazione', 'Utente',
    'Oggetto', 'Descrizione', 'Note',
    'File', 'Est.', 'Creazione',
    ]
width = [
    10, 5,
    30, 10, 10,
    12, 12,
    25, 20, 20, 
    25, 25, 25, 25,
    40, 40, 40,
    20, 10,
    ]

ws_name = 'Docnaet'
WB.create_worksheet(ws_name)
WB.column_width(ws_name, width)

# Header:
row = 0
WB.write_xls_line(ws_name, row, header, excel_format['f_text'])

for key in sorted(database['document'], key=lambda x: (
        x['docAzienda'], 
        x['ID_protocollo'], 
        x['docNumero'], 
        )):
        
    row += 1
    item = database['document'][key]
        
    item_id = item['ID_documento']
    protocol_id = item['ID_protocollo']
    # database['protocol'].get(protocol_id),
    language_id = item['ID_lingua']
    type_id = item['ID_tipologia']
    user_id = item['ID_utente']
    application_id = ''    
    partner_id = item['ID_cliente']
    category_id = '' #item['ID_cliente']
    country_id = ''
    link = ''  # TODO 
    
    # Campi non usati:
    # support_id = item['ID_supporto']
    deadlined = item['docScaduto']
    suspended = item['docSospeso']
    suspended_reason = item['docMotivo']
    access = item['docAccesso']
    check = item['docControllo']

    data = [
        'APRI', 
        link,  # 
        item['docAzienda'],
        protocol_id, item['docNumero'], item['docFax'], 
        item['docData'], item['docScadenza'],         
        partner_id, category_id, country_id,         
        type_id, language_id, application_id, user_id,        
        item['docOggetto'], item['docDescrizione'], item['docNote'],
        item['docFile'], item['docEstensione'], item['docCreazioneEffettiva'],              
    ]

    # TODO change (manage link):
    filename = '%s.%s' % (item_id, extension) 
    fullname = os.path.join(root_path, protocol_id, filename)
    url = 'file://%s' % fullname
    WB.write_xls_line(ws_name, row, data, excel_format['f_text'])
    cell = WB.rowcol_to_cell(row, 0)
    WB.write_url(ws_name, cell, url, string='Apri documento')        
WB.close_workbook()
