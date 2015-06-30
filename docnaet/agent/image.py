#!/usr/bin/python
import os
#import sys
#import subprocess

# Parameters:
image_path = "C:\\Fashion\\image"
default_program = True
default_program_command = "c:\\windows\\system32\\mspaint.exe"

if len(sys.argv) != 2:
    print("Not all parameters!")
    sys.exit()

argument = sys.argv[1].split('//')[-1].split("/")
subpath = argument[0]
image = argument[1]

image_path = "%s\\%s\\" % (image_path,  subpath)
if default_program:
   command ="start %s%s" %(image_path, image)
else:
   command = "'%s' %s%s" %(default_program_command, image_path, image)

os.system(command)

#subprocess.call(["start", image], shell=True)
#subprocess.call(["open", image])
#subprocess.Popen(["start", image])

