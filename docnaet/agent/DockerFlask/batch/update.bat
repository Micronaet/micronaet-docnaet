rem Run this batch in folder where Dockerfile is!

rem Parameters:
SET docker_folder=c:\Micronaet\Docker
SET root_folder=%docker_folder%\DockerFlask
SET git_folder=%docker_folder%\git\micronaet-docnaet
SET data_folder=%root_folder%\data

rem Update from git:
mkdir "%git_folder%"
git pull

rem Create Docker environment
xcopy %git_folder%\docnaet\agent\DockerFlask\* %root_folder%\* /e/d/y
mkdir %data_folder%
cd %root_folder%

rem Stop, delete container, remove image:
docker stop docnaet-agent
docker rm docnaet-agent
docker rmi docnaet-agent

rem Create new image from Dockerfile:
docker build --tag docnaet-agent-flask .

rem Restart new container:
docker run -it -p 5000:5000 --name=docnaet-agent --hostname=docnaet -v %data_folder%:/app/data --restart=always docnaet-agent-flask
rem docker run -d -p 5000:5000 --name=docnaet-agent --hostname=docnaet -v %data_folder%:/app/data --restart=always docnaet-agent-flask

rem Show started container:
docker ps -a
