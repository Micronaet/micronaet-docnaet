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

rem Install
%pip_command% install --no-cache-dir --upgrade -r %requirements%

rem Create Docker environment
xcopy %git_folder%\docnaet\agent\Flask\* %app_folder%\* /e/d/y
mkdir %data_folder%
pause
cd %app_folder%
%python_command% %app_folder%\openerp.py

