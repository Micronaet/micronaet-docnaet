#!/usr/bin/python
import os
import sys
#import subprocess

# Parameters:
# TODO parametrize:
docnaet_path = 'C:\\Docnaet\\FileStore'
docnaet_log = 'C:\\Docnaet\\Log\\docnaet.log'
f_log = open(docnaet_log, 'a')

if len(sys.argv) != 2:
    f_log.write('Not all parameters: %s\n' % (sys.argv))
    sys.exit()

# -----------------------------------------------------------------------------
# Extract operation from arguments:
# -----------------------------------------------------------------------------
# Format: docnaet://[operation]parameters
argument = sys.argv[1].split('//')[-1].split(']')
operation = argument[0][1:] # remove [
parameter = argument[1][:-1] # remove /

# -----------------------------------------------------------------------------
# Web Services:
# -----------------------------------------------------------------------------
if operation == 'open':
    # Extract parameters:
    parameters = parameter.split('-')
    protocol_id = parameters[0]
    document_id = parameters[1]
    
    # real: document = os.path.join(docnaet_path, document_id)
    # temp:
    document = os.path.join(docnaet_path, protocol_id, document_id) 
    command = 'start %s' % document
    f_log.write('Command %s: %s\n' % (operation, command))
    try:
        os.system(command)
    except:
        f_log.write('Error launch command %s\n' % (sys.exc_info(), ))
    
elif operation == 'home':
    pass # TODO
