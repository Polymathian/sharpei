FROM python:3.6-slim

COPY . /app
WORKDIR /app

RUN mkdir /data
RUN pip3 install -e .

ENTRYPOINT [ "sharpei",  "/data"]