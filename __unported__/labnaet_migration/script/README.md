===============================================================================
Installazione dipendenze per accedere direttamente ad access:
===============================================================================

sudo apt-get install unixodbc-dev
sudo apt-get install python-pip
pip install pyodbc


import pyodbc

DBfile = '/data/MSAccess/Music_Library.mdb'
conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ='+DBfile)
#use below conn if using with Access 2007, 2010 .accdb file
#conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+DBfile)
cursor = conn.cursor()

SQL = 'SELECT Artist, AlbumName FROM RecordCollection ORDER BY Year;'
for row in cursor.execute(SQL): # cursors are iterable
    print row.Artist, row.AlbumName
    # print row # if print row it will return tuple of all fields

cursor.close()
conn.close()

from meza import 
