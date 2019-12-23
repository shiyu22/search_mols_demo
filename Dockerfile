From conda/miniconda3

WORKDIR /app/src
COPY . /app

RUN apt-get update
RUN pip install -r /app/requirements.txt
RUN conda install -y -c rdkit rdkit

RUN mkdir -p /tmp/result-mols

CMD python app.py
