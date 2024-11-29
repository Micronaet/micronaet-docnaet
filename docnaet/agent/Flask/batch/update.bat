rem Run this batch in folder where Dockerfile is!

rem Parameters:
SET micronaet_folder=C:\Micronaet
SET app_folder=%micronaet_folder\Docnaet\Flask
SET git_folder=%root_folder%\git\micronaet-docnaet
SET data_folder=%app_folder%\Data

SET python_folder=C:\Python2.7
SET python_command=%python_folder%\python.exe

rem Update from git:
cd %git_folder%
git pull

rem Create Docker environment
xcopy %git_folder%\docnaet\agent\Flask\* %app_folder%\* /e/d/y
mkdir %data_folder%
cd %app_folder%

pause
