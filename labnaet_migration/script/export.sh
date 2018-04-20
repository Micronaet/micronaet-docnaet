#!/bin/bash
for table in $(mdb-tables docnaet.mdb)
   do 
      mdb-export docnaet.mdb ${table} > ./import/${table}.txt
   done   
   
