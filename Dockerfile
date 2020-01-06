From ubuntu

WORKDIR /app/src
COPY . /app

RUN apt-get update

RUN mkdir -p /tmp/result-mols
