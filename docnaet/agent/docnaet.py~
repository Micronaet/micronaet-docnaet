#!/usr/bin/python
import os
#import sys
#import subprocess

# Parameters:
import pdb; pdb.set_trace()
image_path = "C:\\Docnaet\\Filestore"

if len(sys.argv) != 2:
    print("Not all parameters!")
    sys.exit()

argument = sys.argv[1].split('//')[-1].split("/")
subpath = argument[0]
image = argument[1]

image_path = "%s\\%s\\" % (image_path,  subpath)
command ="start %s%s" %(image_path, image)
os.system(command)

#subprocess.call(["start", image], shell=True)
#subprocess.call(["open", image])
#subprocess.Popen(["start", image])

