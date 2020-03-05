import logging
from common.const import default_cache_dir
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index
from diskcache import Cache
from encoder.encode import smiles_to_vec
import psycopg2


PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "zilliz"
PG_PASSWORD = "zilliz"
PG_DATABASE = "milvus"


def connect_postgres_server():
    try:
        conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD, database=PG_DATABASE)
        print("connect the database!")
        return conn
    except:
        print("unable to connect to the database")


def search_loc_in_pg(cur, ids, table_name):
    try:
        sql = "select smiles from " + table_name+ " where ids = '" + str(ids) + "';"
        cur.execute(sql)
        rows = cur.fetchall()
        return str(rows[0][0])
    except:
        print("search faild!")


def do_search(table_name, molecular_name, top_k):
    try:
        feats = []
        index_client = milvus_client()
        feat = smiles_to_vec(molecular_name)
        feats.append(feat)
        status, vectors = search_vectors(index_client, table_name, feats, top_k)
        # print(status)
        vids = [x.id for x in vectors[0]]

        conn = connect_postgres_server()
        cur = conn.cursor()
        res_smi = []
        for i in vids:
            index = search_loc_in_pg(cur, i, table_name)
            res_smi.append(index)

        return res_smi

    except Exception as e:
        logging.error(e)
        return "Fail with error {}".format(e)
    finally:
        if index_client:
            index_client.disconnect()
        cur.close()
        conn.close()
