import os

path = './'
extensions = [
    'xls', 'xlsx',
    'doc', 'docx',
    'pdf',
    # 'pub',
    # 'ppt', 'pptx',
    # 'pps', 'ppsx',
    # 'zip',
]

files = []
for root, folders, files in os.walk(path):
    for file in files:
        extension = file.split('.')[-1].lower()
        fullname = os.path.join(root, file)
        if extension in extensions:
            print(fullname)
        else:
            print('[Jumped] %s' % fullname.replace('/', '|*|'))
