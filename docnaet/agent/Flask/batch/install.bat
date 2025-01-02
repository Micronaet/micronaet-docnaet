@echo off
rem Run this batch in folder where Dockerfile is!

rem Parameters:
SET micronaet_folder=C:\Micronaet
SET app_folder=%micronaet_folder%\Docnaet\Flask
SET git_folder=%micronaet_folder%\git\micronaet-docnaet
SET data_folder=%app_folder%\Data
SET requirements=%app_folder%\requirements.txt

SET python_folder=C:\Python313
SET python_command=%python_folder%\python.exe
SET pip_command=%python_folder%\Scripts\pip.exe

rem Update from git:
cd %git_folder%
git pull

rem Install requirements:
%pip_command% install --no-cache-dir --upgrade -r %requirements%

rem Create Docker environment
xcopy %git_folder%\docnaet\agent\Flask\* %app_folder%\* /e /d /y
xcopy %git_folder%\docnaet\agent\Flask\openerp.py %app_folder%\openerp.pyw /e /d /y
mkdir %data_folder%

rem Open app folder:
explorer %git_folder%\docnaet\agent\Flask\openerp.py %app_folder%

rem Open Esecuzione automatica folder
explorer "%appdata%\microsoft\windows\start menu\programmi\esecuzione automatica"

rem Open Data folder for config file
explorer %data_folder%

rem Launch application for test (after run as pyw)
cd %app_folder%
%python_command% %app_folder%\openerp.py
