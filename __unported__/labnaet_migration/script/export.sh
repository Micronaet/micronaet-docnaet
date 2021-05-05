#!/bin/bash
for table in $(mdb-tables labnaet.mdb)
   do 
      mdb-export labnaet.mdb ${table} > ./import/${table}.txt
   done   
   
