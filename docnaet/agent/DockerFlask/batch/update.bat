rem Run this batch in folder where Dockerfile is!

rem Parameters:
docker_folder=c:\Micronaet\Docker
root_folder=%docker_folder%\DockerFlask
git_folder=%docker_folder%\git\micronaet-docnaet
data_folder=%root_folder%\data

rem Update from git:
mkdir %git_folder%
git pull

rem Create Docker environment
copy /s/d %git_folder%\docnaet\client\DockerFlask %root_folder%\
mkdir %data_folder%
cd %root_folder%

rem Stop, delete container, remove image:
docker stop docnaet-agent-flask
docker rm docnaet-agent-flask
docker rmi docnaet-agent-flask

# Create new image from Dockerfile:
docker build --tag docnaet-agent-flask .

# Restart new container:
docker run -d -p 5000:5000 --name=docnaet-agent --hostname=docnaet -v %data_folder%:/docnaet/data --restart=always docnaet-agent-flask

# Show started container:
docker ps -a
