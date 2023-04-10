# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /yugioh-swiss-pairings-api

COPY requirements-dev.txt requirements-dev.txt
RUN pip3 install -r requirements-dev.txt

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]