import os
import os.path as path
import logging
from common.config import DATA_PATH, DEFAULT_TABLE
from common.const import UPLOAD_PATH
from common.const import default_cache_dir
from common.const import UPLOAD_PATH
from service.load import do_load
from service.search import do_search
from service.count import do_count
from service.delete import do_delete
from service.theardpool import thread_runner
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index
from flask_cors import CORS
from flask import Flask, request, send_file, jsonify
from flask_restful import reqparse
from werkzeug.utils import secure_filename
import numpy as np
from numpy import linalg as LA
from diskcache import Cache
import shutil
import urllib
import os
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit.Chem import Draw


app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['jpg', 'png'])
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
app.config['JSON_SORT_KEYS'] = False
CORS(app)

model = None


@app.route('/api/v1/load', methods=['POST'])
def do_load_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        add_argument('File', type=str). \
        parse_args()
    table_name = args['Table']
    file_path = args['File']
    try:
        thread_runner(1, do_load, table_name, file_path)
        return "Start"
    except Exception as e:
        return "Error with {}".format(e)


@app.route('/api/v1/delete', methods=['POST'])
def do_delete_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        parse_args()
    table_name = args['Table']
    print("delete table.")
    status = do_delete(table_name)
    return "{}".format(status)


@app.route('/api/v1/count', methods=['POST'])
def do_count_api():
    args = reqparse.RequestParser(). \
        add_argument('Table', type=str). \
        parse_args()
    table_name = args['Table']
    rows = do_count(table_name)
    return "{}".format(rows)


@app.route('/api/v1/process')
def thread_status_api():
    cache = Cache(default_cache_dir)
    return "current: {}, total: {}".format(cache['current'], cache['total'])


@app.route('/data/<image_name>')
def image_path(image_name):
    file_name = UPLOAD_PATH + '/' + image_name
    if path.exists(file_name):
        return send_file(file_name)
    return "file not exist"


@app.route('/api/v1/search', methods=['POST'])
def do_search_api():
    args = reqparse.RequestParser(). \
        add_argument("Table", type=str). \
        add_argument("Num", type=int, default=1). \
        add_argument("Molecular", type=str). \
        parse_args()

    table_name = args['Table']
    if not table_name:
        table_name = DEFAULT_TABLE
    top_k = args['Num']
    molecular_name = args['Molecular']
    if not molecular_name:
        return "no molecular"
    if molecular_name:
        res_smi,res_distance = do_search(table_name, molecular_name, top_k)
        res_mol = []
        for i in range(len(res_smi)):
            mol = Chem.MolFromSmiles(res_smi[i])
            res_mol.append(mol)
        print("res_mol:",len(res_mol))
        test = ["%s%s" % (res_smi[x]+'\n' , str(res_distance[x])) for x in range(len(res_mol))]
        print(test)
        # img = Draw.MolsToGridImage(res_mol, molsPerRow=2, subImgSize=(400, 400),legends=["%s%s" % (res_smi[x]+'\n' , str(res_distance[x])) for x in range(len(res_mol))])
        img = Draw.MolsToGridImage(res_mol, molsPerRow=2, subImgSize=(400, 400),legends=test)
        img.save(UPLOAD_PATH + "/similarities_results.png")
        res_img = request.url_root + "data/similarities_results.png"
        return jsonify(res_img), 200
    return "not found", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0")
