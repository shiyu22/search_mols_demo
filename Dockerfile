From conda/miniconda3-centos7

WORKDIR /app
COPY . /app

RUN apt-get update

RUN conda update -n base -c defaults conda
RUN conda install -c rdkit rdkit -y
RUN pip install -r /app/requirements.txt

RUN mkdir -p /tmp/result-mols
