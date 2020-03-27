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

    delta_days = datetime.timedelta(days=days)
    #changing the variable name in the edit
    secs = int(24 * 60 * 60 * portion)
    delta_deconds = datetime.timedelta(seconds=secs)
    result = (start_date + delta_days + delta_seconds)
    return result.strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
sheet_exclude = ['INDICE']
# From config file:
cfg_file = os.path.expanduser('./openerp.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
dbname = config.get('dbaccess', 'dbname')
user = config.get('dbaccess', 'user')
pwd = config.get('dbaccess', 'pwd')
server = config.get('dbaccess', 'server')
port = config.get('dbaccess', 'port')

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
document_pool = odoo.model('docnaet.document')
for root, folders, files in os.walk(path):
    for f in files:        
        if f.split('.')[-1] not in ('xls', 'xlsx'):
            print 'File not used: %s' % f
            continue
        
        if f not in selected_files:
            print 'File not in selection: %s' % f
            continue

        xls_file = os.path.join(path, f)        
        if xls_file not in log_db:
            log_db[xls_file] = {}
        wb = xlrd.open_workbook(xls_file)
        for ws_name in wb.sheet_names():
            if ws_name in sheet_exclude:
                print 'Sheet excluded: %s' % ws_name
                continue
                
            partner_code = ws_name.split()[-1].strip()
            if not(partner_code[:2].isdigit() and partner_code[3:].isdigit() and \
                partner[2:3] = '.'):
                print 'No partner code found in sheet: %s' % ws_name
                continue

            # TODO Search partner

            if ws_name not in log_db[xls_file]:
                log_db[xls_file][ws_name] = {}
                   
            ws = wb.sheet_by_name(ws_name)
            for position in ws.hyperlink_map:
                row, col = position
                try:
                    cell = ws.cell(row, col)
                except:
                    print 'Cell not found', f, ws_name, row, col
                    continue
                
                link = ws.hyperlink_map[position]
                if link.type != 'url':
                    continue

                file_link = os.path.join(path, link.url_or_path)
                import pdb; pdb.set_trace()                
                if file_link not in log_db[xls_file][ws_name]:
                    log_db[xls_file][ws_name][file_link] = False # Docnaet ID
                    
                date_value = xldate_to_datetime(cell.value)
                print 'Partner: %s, Sheet: %s, [%s:%s], Date: %s, Link %s' % (
                    partner_id,
                    ws_name, 
                    row, 
                    col, 
                    date_value, 
                    file_link,
                    )
pickle.dump(open(pickle_file, 'wb'))
