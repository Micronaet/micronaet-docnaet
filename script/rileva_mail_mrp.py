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
import xlsxwriter
import ConfigParser

import smtplib
from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
# Excel file: 
file_out = 'carichi_di_produzione.xlsx'

now = ('%s' % datetime.now())[:19]

# From config file:
cfg_file = os.path.expanduser('./openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')   # verify if it's necessary: getint

mail_recipients = config.get('smtp', 'to')
mail_text = 'Dettaglio carichi di produzione: Generato il {}'.format(now)
mail_subject = 'Dettaglio carico con sviluppo costi da MP, Imballi e costo linea.'


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
mailer = odoo.model('ir.mail_server')

load_pool = odoo.model('mrp.production.workcenter.line')

# Excel:
WB = xlsxwriter.Workbook(file_out)
WS = WB.add_worksheet('Carichi')

# Header
row = 0
WS.write(row, 0, 'Codice')
WS.write(row, 1, 'Prodotto')
WS.write(row, 2, 'Produzione')
WS.write(row, 3, 'Data')
WS.write(row, 4, 'Q.')
WS.write(row, 5, 'Costo')
WS.write(row, 6, 'Dettaglio')

load_ids = load_pool.search([
    ('product_price_calc', '!=', False),
    ])
    
total = len(load_ids)
loads = sorted(
    load_pool.browse(load_ids), 
    key=lambda x: x.date_start,
    reverse=True
)
WS.set_default_row(20)
for load in loads:
    row += 1
    if not row % 10:
        print('Write %s of %s' % (row, total))
    product = load.product
    detail = load.product_price_calc
    medium = detail.split('<b>')[-1][:-4]

    # Data
    WS.write(row, 0, product.default_code)
    WS.write(row, 1, product.name)
    WS.write(row, 2, load.production_id.name)
    WS.write(row, 3, load.date_start)
    WS.write(row, 4, load.qty)
    WS.write(row, 5, medium)
    WS.write(row, 6, detail.replace('<br>', '\n').replace(
        '<br/>', '\n').replace(
            '<b>', '').replace(
                '</b>', ''))
    
try:
    WB.close()
except:
    print('Errore chiudendo file XLSX')

# -----------------------------------------------------------------------------
#                                  SMTP Sent:
# -----------------------------------------------------------------------------
# Get mailserver option:
mailer_ids = mailer.search([
    ('name', '=', 'PCA'),
    ])
if not mailer_ids:
    print('[ERR] No mail server configured in ODOO')
    sys.exit()

odoo_mailer = mailer.browse(mailer_ids)[0]

# Open connection:
print('[INFO] Sending using "%s" connection [%s:%s]' % (
    odoo_mailer.name,
    odoo_mailer.smtp_host,
    odoo_mailer.smtp_port,
    ))

if odoo_mailer.smtp_encryption in ('ssl', 'starttls'):
    smtp_server = smtplib.SMTP_SSL(
        odoo_mailer.smtp_host, odoo_mailer.smtp_port)
else:
    print('[ERR] Connect only SMTP SSL server!')
    sys.exit()
    # server_smtp.start() # TODO Check

smtp_server.login(odoo_mailer.smtp_user, odoo_mailer.smtp_pass)
for to in mail_recipients.replace(' ', '').split(','):
    print('Sending mail to: %s ...' % to)
    msg = MIMEMultipart()
    msg['Subject'] = mail_subject
    msg['From'] = odoo_mailer.smtp_user
    msg['To'] = mail_recipients
    msg.attach(MIMEText(mail_text, 'html'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(file_out, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition', 'attachment; filename="%s"' % file_out)
    msg.attach(part)

    # Send mail:
    smtp_server.sendmail(odoo_mailer.smtp_user, to, msg.as_string())
smtp_server.quit()
