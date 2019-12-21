import os
import os.path as path
import logging
from common.config import DATA_PATH, DEFAULT_TABLE
from common.const import UPLOAD_PATH
# from common.const import input_shape
from common.const import default_cache_dir
from service.load import do_load
from service.search import do_search
from service.count import do_count
from service.delete import do_delete
from service.theardpool import thread_runner
# from preprocessor.vggnet import vgg_extract_feat
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index
from flask_cors import CORS
from flask import Flask, request, send_file, jsonify
from flask_restful import reqparse
from werkzeug.utils import secure_filename
# from keras.applications.vgg16 import VGG16
# from keras.applications.vgg16 import preprocess_input as preprocess_input_vgg
# from keras.preprocessing import image
import numpy as np
from numpy import linalg as LA
# import tensorflow as tf
# from tensorflow.python.keras.backend import set_session
# from tensorflow.python.keras.models import load_model
from diskcache import Cache
import shutil
import urllib
import os
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit.Chem import Draw

# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.3
# global sess
# sess = tf.Session(config=config)
# set_session(sess)

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['jpg', 'png'])
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
app.config['JSON_SORT_KEYS'] = False
CORS(app)

model = None

# def load_model():
#     global graph
#     graph = tf.get_default_graph()

#     global model
#     model = VGG16(weights='imagenet',
#                   input_shape=input_shape,
#                   pooling='max',
#                   include_top=False)


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
    try:
        shutil.rmtree(DATA_PATH)
    except:
        print("cannot remove", DATA_PATH)
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
    file_name = DATA_PATH + '/' + image_name
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

        img = Draw.MolsToGridImage([res_mol], molsPerRow=2, subImgSize=(400, 400),legends=["%s - %f" % (res_smi[x], res_distance[x]) for x in range(len(res_mol))])
        img.save("../out/similarities_results.png")
        res_img = request.url_root +"out/similarities_results.png"        
        print(res_img)
        return jsonify(res_img), 200
    return "not found", 400


if __name__ == "__main__":
    # load_model()
    app.run(host="0.0.0.0")
