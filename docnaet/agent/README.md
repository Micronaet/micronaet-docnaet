Docnaet Agent:
==============
Agent for open directly network document via SMB sharing

Windows only:

1. reg files active docnaet:// type of link
2. python files open document and is executed from docnaet://*
3. Copy folder in c:\ (as docnaet)
4. Modify config file for set up the correct path
5. Modify bat with call to python


Note:
to convert all image with lower case use:
for i in *.jpg; do mv "$i" $(echo "$i" | awk -F '.jpg' '{ print tolower($1) FS }'); done

**TODO:** Implement also for linux: https://support.shotgunsoftware.com/entries/86754-How-to-launch-external-applications-using-custom-protocols-rock-instead-of-http-
