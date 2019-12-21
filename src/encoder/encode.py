import os
import numpy as np
from common.config import DATA_PATH as database_path
from diskcache import Cache
from rdkit import DataStructs
from common.const import default_cache_dir
from rdkit import Chem
import math
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
    print("mols:",mols)
    fp = AllChem.GetMorganFingerprintAsBitVect(mols, 2, VECTOR_DIMENSION)
    print("fp:",fp)
    hex_fp = DataStructs.BitVectToFPSText(fp)
    print("hex_fp:",hex_fp)
    bstr = hex_to_bin(hex_fp)
    print("bstr:",bstr)
    vec = bin_to_vec(bstr)
    print("vec:",vec)
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
            print(str(line))
            # line = 'o1c(C(O)CNC(C)(C)C)cc2c1c(CC(=O)OC(C)(C)C)ccc2'
            # try:
            vec = smiles_to_vec(line)
            print(vet)
            feats.append(f)
            names.append(line)
            # except:
            #     continue
        print ("extracting feature from smi No. %d , %d images in total" %(current, total))
    return feats, names