#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import ConfigParser

# -----------------------------------------------------------------------------
#                                Parameters
# -----------------------------------------------------------------------------
# Config file (home folder of current user):
cfg_file = os.path.expanduser(os.path.join('~', 'openerp.cfg'))
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# Folder:
store_path = config.get('folder', 'store_path')
private_path = config.get('folder', 'private_path')

# Command
protocol = config.get('command', 'protocol')
separator = config.get('command', 'separator')
folder_command = config.get('command', 'folder_command')
openfile_command = config.get('command', 'openfile_command')

# Log:
log_file = config.get('log', 'file')

log_f = open(log_file, 'a')

# ----------------------------------------------------------------------------
# Parse elements:
# ----------------------------------------------------------------------------
command = sys.argv[1][len(protocol):].split(separator)
if len(command) != 2:
    log_f.write('Not enought parameters\n')
    log_f.close()
    sys.exit()

operation, argument = command

# ----------------------------------------------------------------------------
# Operations: 
# ----------------------------------------------------------------------------
# -------------
# 1. Open file:
# -------------
if operation == 'document':
    filename = os.path.join(store_path, argument)
    log_f.write('Open doc: %s\n' % filename)
    log_f.close()
    os.system(openfile_command % filename)

# ---------------
# 2. Open folder:
# ---------------
elif operation == 'folder':
    folder = os.path.join(private_path, argument)       
    if folder[-1] == '/':
        folder = folder[:-1]
    log_f.write('Open user folder: %s\n' % folder)
    log_f.close()
    os.system('%s %s' % (folder_command, folder))

# -----------------------------
# E: Error no correct operation
# -----------------------------
else:
    log_f.write('Error not managed operation: %s\n' % operation)
    log_f.close()
    





