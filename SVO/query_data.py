from mymodel import *
import numpy as np

f = open(sys.argv[1])
embeddings = cPickle.load(f)
leftop = cPickle.load(f)
rightop = cPickle.load(f)
simfn = cPickle.load(f)
f.close()


ents=embeddings[0].E.get_value()
r_mats=embeddings[1].E.get_value()
r_vecs=embeddings[2].E.get_value()


a=cPickle.load(open('../data/SVO_idx2entity.pkl'))
nrel=4547

new_E={}
for i in range(len(ents[0])-nrel):
	new_E[a[i]]=ents[:,i]

new_R={}
for i in range(nrel):
	new_R[a[i+len(ents[0])-nrel]]=[r_mats[:,i],r_vecs[:,i]]


#cPickle.dump([new_E,new_R],open('essai_data.pkl','w'))

def closest(entity, k=10, rel=None, repeat=1):
	vect1 = new_E[entity]
	if rel is None:
		dists = sorted((np.sum(np.abs(v-vect1)), e) for e,v in new_E.iteritems())
	else:
		dists = sorted((np.sum(np.abs(new_R[rel][0] *(v-vect1)-new_R[rel][1])), e) for e,v in new_E.iteritems())
	return [e for norm, e in dists[:k]]

def find_entity(name):
	return [e for e in new_E if "__%s_"%name in e]


