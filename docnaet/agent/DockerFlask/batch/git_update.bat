rem Run this batch in folder where Dockerfile is!

rem Parameters:
SET docker_folder=c:\Micronaet\Docker
SET root_folder=%docker_folder%\DockerFlask
SET git_folder=%docker_folder%\git\micronaet-docnaet

rem Update from git:
mkdir "%git_folder%"
git pull
pause
