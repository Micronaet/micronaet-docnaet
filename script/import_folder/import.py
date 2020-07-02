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
import erppeek
import ConfigParser
import time
import shutil
from datetime import datetime
import pdb

# ----------------
# Read parameters:
# ----------------
company_id = 1
partner_id = 1
user_id = 1
priority_id = 3
protocol_id = 20
language_id = 1
type_id = False
sector_id = 3

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
print('Connecting ODOO %s: %s:%s' % (dbname, server, port))

# Pool used:
docnaet_pool = erp.DocnaetDocument
program_pool = erp.DocnaetProtocolTemplateProgram

# -----------------------------------------------------------------------------
# Load data:
# -----------------------------------------------------------------------------
program_db = {}
program_ids = program_pool.search([])
for program in program_pool.browse(program_ids):
    program_db[program.extension] = program.id

# TODO Attenzione ai documenti puntatori (doppio ciclo per assegnazione parent)
print('Read filesystem: %s' % filesystem_path)
remove_left = len(filesystem_path) + 1
for root, folders, files in os.walk(filesystem_path):
    for filename in files:
        name_part = filename.split('.')
        extension = name_part[-1].lower()
        if extension not in program_db:
            print('Extension not used: %s' % filename)
            continue
        fullname = os.path.join(root, filename)
        create_date = get_create_date(fullname)
        name = '.'.join(name_part[:-1])
        description = '%s (Tipo: %s)' % (
            fullname[remove_left:-len(extension) - 1].replace('/', ' >> '),
            extension,
        )

        note = 'Importato con procedure automatica [%s]' % \
               datetime.now()

        program_id = program_db.get(extension)
        if not program_id:
            print('Extension non found: %s' % extension)

        # Create / Update operations:
        data = {
            'company_id': company_id,
            'partner_id': partner_id,
            'user_id': user_id,
            'protocol_id': protocol_id,
            'language_id': language_id,
            'program_id': program_id,
            'sector_id': sector_id,
            'type_id': type_id,
            'date': create_date,
            'name': name,
            'description': description,
            'note': note,
            # 'number': number,
            'docnaet_extension': extension,
            }

        document_ids = docnaet_pool.search([
            ('description', '=', description),
            ])
        if document_ids:
            # Update
            docnaet_pool.write(document_ids, data)
            print('Update record %s' % description)
            docnaet_id = document_ids[0]
            # continue # File yet present!?!
        else:
            # Create
            docnaet_id = docnaet_pool.create(data).id
            print('Create record %s' % description)
        docnaet_fullname = os.path.join(docnaet_path, '%s.%s' % (
            docnaet_id, extension))
        print('   Import file: %s > %s' % (fullname, docnaet_fullname))
        shutil.copy(fullname, docnaet_fullname)

        try:
            erp.exec_workflow(
                'docnaet.document',
                'document_draft_confirmed',
                docnaet_id)
            print('Confermato WF')
        except:
            print('Non confermato WF, già corretto')
