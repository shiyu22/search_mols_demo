From conda/miniconda3

WORKDIR /app/src
COPY . /app

RUN mkdir -p /tmp/result-mols

RUN apt-get update
RUN pip install -r /app/requirements.txt