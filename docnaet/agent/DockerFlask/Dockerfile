# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

LABEL version="0.1"
LABEL maintaner="Micronaet - Nicola Riolini"
LABEL release-date="2024-11-29"

WORKDIR /app/data
WORKDIR /app

# ENV data_folder=/app/data
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./app/requirements.txt requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
COPY ./app/. ./
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "-p", "5000"]

