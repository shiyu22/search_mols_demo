import os
import numpy as np
from common.config import DATA_PATH as database_path
from diskcache import Cache
from common.const import default_cache_dir
from rdkit import Chem
from rdkit.Chem import AllChem
from common.config import VECTOR_DIMENSION


def hex_to_bin(fp):
    length = len(fp) * 4
    bstr = str(bin(int(fp,16)))
    bstr = (length-(len(bstr)-2)) * '0' + bstr[2:]
    return bstr


def bin_to_vec(bstr):
    vec = []
    for f in bstr:
        f = int(f) * 1.0
        vec.append(f)
    return vec


def smiles_to_vec(smiles):
    mols = Chem.MolFromSmiles(smiles)
    fp = AllChemcd .GetMorganFingerprintAsBitVect(mols, 2, VECTOR_DIMENSION)
    hex_fp = DataStructs.BitVectToFPSText(fp)
    bstr = hex_to_bin(hex_fp)
    vec = bin_to_vec(bstr)
    return vec


def feature_extract(table_name, filepath, names = [], feats = []):
    cache = Cache(default_cache_dir)
    total = len(open(filepath,'rU').readlines())
    cache['total'] = total
    current = 0
    with open(filepath, 'r') as f:
        for line in f:
            current += 1
            cache['current'] = current
            line = line.strip()
            # try:
            vec = smiles_to_vec(line)
            feats.append(f)
            names.append(line)
            # except:
            #     continue
        print ("extracting feature from smi No. %d , %d images in total" %(current, total))
    return feats, names