FROM python:3.9-slim-buster

COPY . /app
WORKDIR /app

RUN mkdir /data
RUN pip3 install -e .

ENTRYPOINT [ "sharpei",  "/data"]