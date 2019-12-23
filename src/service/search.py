import logging
from common.const import default_cache_dir
from indexer.index import milvus_client, create_table, insert_vectors, delete_table, search_vectors, create_index
# from preprocessor.vggnet import VGGNet
# from preprocessor.vggnet import vgg_extract_feat
from diskcache import Cache
from encoder.encode import smiles_to_vec


def query_smi_from_ids(vids):
    res = []
    cache = Cache(default_cache_dir)
    print("cache:",cache)
    for i in vids:
        if i in cache:
            res.append(cache[i])
    return res


def do_search(table_name, molecular_name, top_k):
    try:
        feats = []
        index_client = milvus_client()
        # feat = vgg_extract_feat(molecular_name, model, graph, sess)
        feat = smiles_to_vec(molecular_name)
        feats.append(feat)
        _, vectors = search_vectors(index_client, table_name, feats, top_k)
        vids = [x.id for x in vectors[0]] #取出查询得到的向量id
        # print(vids)
        # res = [x.decode('utf-8') for x in query_name_from_ids(vids)]

        res_smi = [x for x in query_smi_from_ids(vids)] #取出向量id对应的 .smi 文件
        # print("vids:",vids)
        res_distance = [x.distance for x in vectors[0]] #取出查询得到的向量distance
        # print(res_distance)
        # res = dict(zip(res_id,distance))

        return res_smi,res_distance
    except Exception as e:
        logging.error(e)
        return "Fail with error {}".format(e)
