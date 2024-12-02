Installazione:
- Scarica Git: https://git-scm.com/download/win

- Installarlo e poi scaricare nella cartella:
  C:\Micronaet\git\

- Lanciare git clone https://github.com/Micronaet/micronaet-docnaet

- Lanciare dal repo: 
  C:\Micronaet\git\micronaet-docnaet\docnaet\agent\Flask\batch\install.bat 
  (installa dipendenze, crea la cartella di lavoro)

- Il programma viene lanciato per creare il file di configurazione, modificarlo:
  c:\Micronaet\git\Docnaet\Flask\Dati\openerp.cfg
  Mettere docnaet path: \\10.0.0.200\docnaet$\docnaet\1\store
  Mettere labnaet path: \\10.0.0.200\labnaet$\docnaet\1\store
  
- Impostare l'avvio automatico dal file: 
  c:\Micronaet\git\Docnaet\Flask\openerp.pyw
  in
  "%appdata%\microsoft\windows\start menu\programmi\esecuzione automatica"
  
- Attivare nella gestione utenti di OpenERP / Docnaet la spunta Flask
  
- Lanciare a mano il collegameno e provare ad aprire un file di Docnaet e Labonaet  

- Provare un riavvio PC

