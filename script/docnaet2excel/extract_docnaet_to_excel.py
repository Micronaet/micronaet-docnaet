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
import ConfigParser

# -----------------------------------------------------------------------------
# Parameters:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('./openerp.cfg')
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# SQL:
host = config.get('dbaccess', 'host')
user = config.get('dbaccess', 'user')
password= config.get('dbaccess', 'pwd')
database = config.get('dbaccess', 'dbname')

# Filesystem:
root_path = 'O:' or config.get('filesystem', 'root')  # TODO restore


# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
def clean_text(text):
    """ Clean for Excel
    """
    text = unicode(text or '')
    if text[:1] == '=':
        text = '\'' + text
    return text


# -----------------------------------------------------------------------------
# MS SQL:
# -----------------------------------------------------------------------------
connection = pymssql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    as_dict=True,
)
cr = connection.cursor()

database = {
    'document': [],

    'company': {},
    'important': {},
    'language': {},
    'protocol': {},
    'type': {},
    'user': {},

    'partner': {},
    'partner_type': {},
    'country': {},

    # 'application': {},
    # 'category': {},

    # 'product': {},
    # 'sent': {},
    # 'support': {},
    }

# -----------------------------------------------------------------------------
# Ditte:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Ditte')
for item in cr.fetchall():
    item_id = item['ID_ditta']
    database['company'][item_id] = item['ditRagioneSociale']

# -----------------------------------------------------------------------------
# Protocollo:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Protocolli')
for item in cr.fetchall():
    item_id = item['ID_protocollo']
    database['protocol'][item_id] = item['proDescrizione']

# -----------------------------------------------------------------------------
# Tipologie:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Tipologie')
for item in cr.fetchall():
    item_id = item['ID_tipologia']
    database['type'][item_id] = item['tipDescrizione']

# -----------------------------------------------------------------------------
# Utenti:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Utenti')
for item in cr.fetchall():
    item_id = item['ID_utente']
    database['user'][item_id] = item['uteDescrizione']

# -----------------------------------------------------------------------------
# Lingue:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Lingue')
for item in cr.fetchall():
    item_id = item['ID_lingua']
    database['language'][item_id] = item['linDescrizione']

# -----------------------------------------------------------------------------
#                              Partner:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Clienti')
for item in cr.fetchall():
    item_id = item['ID_cliente']
    database['partner'][item_id] = item

# -----------------------------------------------------------------------------
# Tipo Partner:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Tipologie')
for item in cr.fetchall():
    item_id = item['ID_tipologia']
    database['partner_type'][item_id] = item['tipDescrizione']

# -----------------------------------------------------------------------------
# Nazioni:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Nazioni')
for item in cr.fetchall():
    item_id = item['ID_nazione']
    database['country'][item_id] = item['nazDescrizione']

# -----------------------------------------------------------------------------
#                               Document:
# -----------------------------------------------------------------------------
cr.execute('SELECT * FROM dbo.Documenti')
for item in cr.fetchall():  # TODO remove me
    database['document'].append(item)

# -----------------------------------------------------------------------------
# Generate XLSX files:
# -----------------------------------------------------------------------------
ExcelWriter = excel_export.excel_wrapper.ExcelWriter

excel_db = {}
header = [
    u'APRI', u'Colleg.',
    # u'Azienda',
    # u'Protocollo',
    u'Numero', u'Fax',
    u'Data', u'Scadenza',
    u'Cliente', u'Tipo', u'Nazione',
    u'Tipologia', u'Lingua',
    # u'Applicazione',
    u'Utente',
    u'Oggetto', u'Descrizione', u'Note',
    u'File', u'Est.', 'ID',
    # u'Creazione',
    ]
width = [
    6, 5,
    # 30, 10,
    10, 10,
    18, 18,
    25, 20, 20,
    25, 25, 25,
    # 25,
    40, 40, 40,
    20, 5
    # 10,
    ]

documents = sorted(
    database['document'],
    reverse=True,
    key=lambda x: x['docData'],
    )

# documents = database['document']
for item in documents:

    # -------------------------------------------------------------------------
    # Select WB:
    # -------------------------------------------------------------------------
    company_id = item['docAzienda']
    company = database['company'].get(company_id, '')
    if company_id not in excel_db:
        excel_filename = '/home/openerp7/smb/docnaet/%s.xlsx' % company
        WB = ExcelWriter(excel_filename, verbose=True)
        excel_db[company_id] = {
            'wb': WB,
            'ws': {},
            'format': {
                'f_title': WB.get_format('title'),
                'f_header': WB.get_format('header'),
                'f_text': WB.get_format('text'),
                'f_number': WB.get_format('number'),
                'f_text_red': WB.get_format('bg_red'),
                'f_number_red': WB.get_format('bg_red_number'),
                },
            }
        print('Creating %s' % excel_filename)

    # Readability:
    WB = excel_db[company_id]['wb']
    excel_format = excel_db[company_id]['format']
    WS = excel_db[company_id]['ws']

    # -------------------------------------------------------------------------
    # Select WS:
    # -------------------------------------------------------------------------
    protocol_id = item['ID_protocollo']
    protocol = database['protocol'].get(protocol_id, 'Sconosciuto')
    ws_name = protocol

    if protocol not in WS:
        # Init setup:
        WS[protocol] = 0  # Row
        row = WS[protocol]
        WB.create_worksheet(ws_name)
        WB.column_width(ws_name, width)
        WB.freeze_panes(ws_name, 1, 1)
        WB.autofilter(ws_name, row, 0, row, len(header) - 1)

        # Header:
        WB.write_xls_line(
            ws_name,
            WS[protocol],  # row
            header,
            excel_format['f_header'],
            )
        print('Creating %s >> %s' % (excel_filename, ws_name))

    WS[protocol] += 1
    row = WS[protocol]
    item_id = item['ID_documento']
    language_id = item['ID_lingua']
    type_id = item['ID_tipologia']
    user_id = item['ID_utente']
    partner_id = item['ID_cliente']
    # category_id = ''  # item['ID_cliente']
    # application_id = ''
    link = ''  # TODO
    extension = item['docEstensione']

    # Convert:
    data = '' if not item['docData'] else \
        item['docData'].strftime('%Y-%m-%d %H:%M:%S')
    deadline = '' if not item['docScadenza'] else \
        item['docScadenza'].strftime('%Y-%m-%d %H:%M:%S')

    type_name = database['type'].get(type_id, '')
    language_name = database['language'].get(language_id, '')
    user_name = database['user'].get(user_id, '')
    partner_item = database['partner'].get(partner_id)
    if partner_item:
        partner_name = '%s, %s %s (%s)' % (
            partner_item['cliRagioneSociale'],
            partner_item['cliCAP'],
            partner_item['cliPaese'],
            partner_item['cliProvincia'],
        )
        partner_type_id = partner_item['ID_tipo']
        country_id = partner_item['ID_nazione']

        partner_type_name = excel_db['partner_type'].get(partner_type_id, '')
        country_name = excel_db['country'].get(country_id, '')
        # cliIndirizzo, cliTelefono, cliFax, cliEmail, cliCodice
        # ID_ditta
    else:
        partner_name = ''
        partner_type_name = ''
        country_name = ''

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
        # company,
        # protocol_id,
        item['docNumero'], item['docFax'],
        data, deadline,
        partner_name, partner_type_name, country_name,
        type_name, language_name,
        # application_id,
        user_name,

        clean_text(item['docOggetto']),
        clean_text(item['docDescrizione']),
        clean_text(item['docNote']),

        item['docFile'], extension,
        # item['docCreazioneEffettiva'],
        item['ID_documento'],
    ]
    WB.write_xls_line(ws_name, row, data, excel_format['f_text'])

    # TODO change (manage link):
    filename = '%s.%s' % (item_id, extension)
    fullname = os.path.join(
        root_path, str(company_id), str(protocol_id), filename)
    url = 'file:///%s' % fullname
    cell = WB.rowcol_to_cell(row, 0)
    WB.write_url(ws_name, cell, url, string='APRI')

for company_id in excel_db:
    WB = excel_db[company_id]['wb']
    WB.close_workbook()

