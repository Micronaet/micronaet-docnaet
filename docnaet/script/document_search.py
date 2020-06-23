import os

path = './'
extensions = []

files = []
for root, folders, files in os.walk(path):
    for file in files:
        fullname = os.path.join(root, file)
        print(fullname)
