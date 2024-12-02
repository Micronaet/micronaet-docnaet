rem Parameters:
SET micronaet_folder=C:\Micronaet
SET app_folder=%micronaet_folder%\Docnaet\Flask
SET git_folder=%micronaet_folder%\git\micronaet-docnaet
SET data_folder=%app_folder%\Data
SET requirements=%app_folder%\requirements.txt

SET python_folder=C:\Python313
SET python_command=%python_folder%\python.exe
SET pip_command=%python_folder%\Scripts\pip.exe

SET project=MicroERP

nssm.exe stop %project%
nssm.exe remove %project% confirm

nssm.exe install %project% %python_command% %app_folder%\openerp.py
nssm.exe set %project% AppDirectory %app_folder%

nssm.exe start %project%

pause
