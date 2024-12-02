rem Parameters:
SET micronaet_folder=C:\Micronaet
SET app_folder=%micronaet_folder%\Docnaet\Flask

SET python_folder=C:\Python313
SET python_command=%python_folder%\python.exe

cd %app_folder%
%python_command% %app_folder%\openerp.py

