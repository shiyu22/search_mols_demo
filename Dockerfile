From conda/miniconda3

WORKDIR /app/src
COPY . /app

RUN mkdir -p /tmp/result-mols
