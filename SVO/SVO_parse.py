import os, sys
import cPickle

import numpy as np
import scipy.sparse as sp

# Put the freebase_aaai11 data absolute path here
datapath = sys.argv[1]
assert datapath is not None

if 'data' not in os.listdir('../'):
    os.mkdir('../data')


def parseline(line):
    lhs, rel, rhs = line.split('\t')
    lhs = lhs.split(' ')
    rhs = rhs.split(' ')
    rel = rel.split(' ')
    return lhs, rel, rhs

#################################################
### Creation of the entities/indices dictionnaries

np.random.seed(753)

entlist = []
rellist = []


f = open(datapath + 'svo-nouns.lst', 'r')
dat = f.readlines()
f.close()
for i in dat:
    entlist += [i.strip()]

f = open(datapath + 'svo-verbs.lst', 'r')
dat = f.readlines()
f.close()
for i in dat:
    rellist += [i.strip()]

entset = np.sort(list(set(entlist)))
relset = np.sort(list(set(rellist)))

entity2idx = {}
idx2entity = {}


# we keep the entities specific to one side of the triplets contiguous
idx = 0
for i in entset:
    entity2idx[i] = idx
    idx2entity[idx] = i
    idx += 1
nbent = idx

print "# of  entities: ", nbent
# add relations at the end of the dictionary
for i in relset:
    entity2idx[i] = idx
    idx2entity[idx] = i
    idx += 1
nbrel = idx - (nbent)
print "Number of relations: ", nbrel

f = open('../data/SVO_entity2idx.pkl', 'w')
g = open('../data/SVO_idx2entity.pkl', 'w')
cPickle.dump(entity2idx, f, -1)
cPickle.dump(idx2entity, g, -1)
f.close()
g.close()

#################################################
### Creation of the dataset files

for datatyp,dlen in zip(['train_1000000', 'valid_50000', 'test_250000'],[1000000,50000,250000]):
    f = open(datapath + 'svo_data_%s.dat' % datatyp, 'r')
    dat = f.readlines()[:dlen]
    f.close()

    # Declare the dataset variables
    inpl = sp.lil_matrix((np.max(entity2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpr = sp.lil_matrix((np.max(entity2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpo = sp.lil_matrix((np.max(entity2idx.values()) + 1, len(dat)),
            dtype='float32')
    # Fill the sparse matrices
    ct = 0
    for i in dat:
        lhs, rel, rhs = parseline(i[:-1])
        inpl[int(lhs[0])-1, ct] = 1
        inpr[int(rhs[0])-1, ct] = 1
        inpo[nbent+int(rel[0])-1, ct] = 1
        ct += 1
    # Save the datasets
    if 'data' not in os.listdir('../'):
        os.mkdir('../data')
    f = open('../data/SVO-%s-lhs.pkl' % datatyp[:datatyp.find('_')], 'w')
    g = open('../data/SVO-%s-rhs.pkl' % datatyp[:datatyp.find('_')], 'w')
    h = open('../data/SVO-%s-rel.pkl' % datatyp[:datatyp.find('_')], 'w')
    cPickle.dump(inpl.tocsr(), f, -1)
    cPickle.dump(inpr.tocsr(), g, -1)
    cPickle.dump(inpo.tocsr(), h, -1)
    f.close()
    g.close()
    h.close()
