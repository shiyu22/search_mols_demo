From conda/miniconda3

WORKDIR /app
COPY . /app

RUN apt-get update

RUN conda install -c rdkit nox -y
RUN conda update -n base -c defaults conda
RUN pip install -r /app/requirements.txt

RUN mkdir -p /tmp/result-mols

CMD python ./src/app.py