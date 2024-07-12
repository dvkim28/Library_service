FROM python:3.11.6-alpine3.18
LABEL maintainer="d.villarionovich@gmail.com"

ENV PYTHONBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt



COPY . .

RUN mkdir -p /files/media