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
import pdb
import sys
import shutil
import codecs

block = 1000
dry_run = False
store_folders = [
    ('docnaet', '/home/openerp7/filestore/docnaet/1/store'),
    # '/home/openerp/filestore/labaet/1/store',
    ]

pdb.set_trace()
for mode, store_folder in store_folders:
    print('Moving block files in %s' % store_folder)
    log_f = codecs.open('/tmp/%s.log' % mode, 'w')
    for root, folders, files in os.walk(store_folder):
        for filename in files:
            try:
                document_part = filename.split('.')
                if len(document_part) != 2:
                    print('[ERROR] No document ID: %s' % filename)
                    log_f.write(
                        '[ERROR] No document ID: %s\n' % filename)
                    log_f.flush()
                    continue

                document_id = int(document_part[0])
                folder_ref = str(document_id / block)
            except:
                print('[ERROR] Error parsing, move in error: %s' % filename)
                log_f.write(
                    '[ERROR] Error parsing, move in error: %s\n' % filename)
                log_f.flush()
                folder_ref = 'error'  # Use error folder for no INT files

            block_folder = os.path.join(store_folder, folder_ref)
            os.system('mkdir -p %s' % block_folder)
            # todo setup rights, owner?

            store_fullname = os.path.join(root, filename)
            block_fullname = os.path.join(block_folder, filename)
            message = '[INFO] Move %s in %s' % (
                store_fullname,
                block_fullname,
            )
            print(message)
            log_f.write('%s\n' % message)
            log_f.flush()

            if not dry_run:
                shutil.move(store_fullname, block_fullname)
        break  # Walk only root folder
