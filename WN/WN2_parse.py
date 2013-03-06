import os, sys
import cPickle

import numpy as np
import scipy.sparse as sp

# Put the wordnet-mlj data absolute path here
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



relation_reverse_table={
    '_member_holonym':'_member_meronym',\
    '_synset_domain_region_of':'_member_of_domain_region',\
    '_synset_domain_topic_of':'_member_of_domain_topic',\
    '_has_part': '_part_of',\
    '_synset_domain_usage_of':'_member_of_domain_usage',\
    '_hyponym':'_hypernym',\
    '_substance_holonym':'_substance_meronym',\
    '_instance_hyponym':'_instance_hypernym'}


#################################################
### Creation of the synset/indices dictionnaries

np.random.seed(753)

synlist = []
rellist = []

for datatyp in ['train', 'valid', 'test']:
    f = open(datapath + 'wordnet-mlj12-%s.txt' % datatyp, 'r')
    dat = f.readlines()
    f.close()
    for i in dat:
        lhs, rel, rhs = parseline(i[:-1])
        synlist += [lhs[0], rhs[0]]
        if rel[0] in relation_reverse_table:
            rellist += [relation_reverse_table[rel[0]]]
        else:
            rellist += [rel[0]]


synset = np.sort(list(set(synlist)))
relset = np.sort(list(set(rellist)))

synset2idx = {}
idx2synset = {}

idx = 0
for i in synset:
    synset2idx[i] = idx
    idx2synset[idx] = i
    idx += 1
nbsyn = idx
print "Number of synsets in the dictionary: ", nbsyn
# add relations at the end of the dictionary
for i in relset:
    synset2idx[i] = idx
    idx2synset[idx] = i
    idx += 1
nbrel = idx - nbsyn
print "Number of relations in the dictionary: ", nbrel
#print relset

f = open('../data/WN2_synset2idx.pkl', 'w')
g = open('../data/WN2_idx2synset.pkl', 'w')
cPickle.dump(synset2idx, f, -1)
cPickle.dump(idx2synset, g, -1)
f.close()
g.close()

####################################################
### Creation of the synset definitions dictionnaries

f = open(datapath + 'wordnet-mlj12-definitions.txt', 'r')
dat = f.readlines()
f.close()

synset2def = {}
synset2concept = {}

for i in dat:
    synset, concept, definition = i[:-1].split('\t')
    synset2def.update({synset: definition})
    synset2concept.update({synset: concept})

f = open('../data/WN2_synset2def.pkl', 'w')
g = open('../data/WN2_synset2concept.pkl', 'w')
cPickle.dump(synset2def, f, -1)
cPickle.dump(synset2concept, g, -1)
f.close()
g.close()

#################################################
### Creation of the dataset files

exlist={}

for datatyp in ['train', 'valid', 'test']:
    f = open(datapath + 'wordnet-mlj12-%s.txt' % datatyp, 'r')
    dat = f.readlines()
    f.close()
    exlist[datatyp]=[]
    for i in dat:
        lhs, rel, rhs = parseline(i[:-1])
        if rel[0] in relation_reverse_table:
            exlist[datatyp]+=[rhs[0]+'\t'+relation_reverse_table[rel[0]]+'\t'+lhs[0]]
        else:
            exlist[datatyp]+=[lhs[0]+'\t'+rel[0]+'\t'+rhs[0]]

    exlist[datatyp]=set(exlist[datatyp])
    if datatyp=='valid' or datatyp=='test':
        exlist[datatyp]=list(set(exlist[datatyp]) - set(exlist['train']))

for datatyp in ['train', 'valid', 'test']:
    dat=exlist[datatyp]
    print datatyp, len(dat)
    # Declare the dataset variables
    inpl = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpr = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpo = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    # Fill the sparse matrices
    ct = 0
    for i in dat:
        lhs, rel, rhs = parseline(i)
        inpl[synset2idx[lhs[0]], ct] = 1
        inpr[synset2idx[rhs[0]], ct] = 1
        inpo[synset2idx[rel[0]], ct] = 1
        ct += 1
    # Save the datasets
    if 'data' not in os.listdir('../'):
        os.mkdir('../data')
    f = open('../data/WN2-%s-lhs.pkl' % datatyp, 'w')
    g = open('../data/WN2-%s-rhs.pkl' % datatyp, 'w')
    h = open('../data/WN2-%s-rel.pkl' % datatyp, 'w')
    cPickle.dump(inpl.tocsr(), f, -1)
    cPickle.dump(inpr.tocsr(), g, -1)
    cPickle.dump(inpo.tocsr(), h, -1)
    f.close()
    g.close()
    h.close()
