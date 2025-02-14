Installazione:
- Scarica Git: 
  https://git-scm.com/download/win
  https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe

- Installarlo e poi scaricare nella cartella:
  C:\Micronaet\git\

- Lanciare:
  git clone https://github.com/Micronaet/micronaet-docnaet
 
- Installare Python nella cartella
  Da: C:\Micronaet\git\micronaet-docnaet\docnaet\agent\Flask\batch
  c:\Python313

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
  "%appdata%\microsoft\windows\menu start\programmi\esecuzione automatica"
  
- Attivare nella gestione utenti di OpenERP / Docnaet la spunta Flask
  
- Lanciare a mano il collegameno e provare ad aprire un file di Docnaet e Labonaet  

- Provare un riavvio PC

