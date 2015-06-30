#!/usr/bin/python
import os
import sys
#import subprocess

# Parameters:
import pdb; pdb.set_trace()
# TODO parametrize:
image_path = "C:\\Docnaet\\Filestore"

if len(sys.argv) != 2:
    print("Not all parameters!")
    sys.exit()

# -----------------------------------------------------------------------------
# Extract operation from arguments:
# -----------------------------------------------------------------------------
# Format: docnaet://[operation]parameters
argument = sys.argv[1].split('//')[-1].split("]")
operation = argument[0][1:]
parameter = argument[1]

# -----------------------------------------------------------------------------
# Web Services:
# -----------------------------------------------------------------------------
if operation == 'open':
    # Extract parameters:
    parameters = paramter.split("-")
    protocol_id = parameters[0]
    document_id = parameters[1]
    
    document = os.path.join(image_path, document_id)
    command ="start %s" % docmuent
    os.system(command)
    
elif operation == 'home':
    pass # TODO
    

