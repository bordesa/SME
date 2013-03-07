#! /usr/bin/python

from Tensor_exp import *
from Tensor_evaluation import *

launch(op='Unstructured', dataset='umls', fold=0, simfn='Dot', Nent=184, Nrel=49, marge=1., lremb=0.1,
    lrparam=0.1, nbatches=100, totepochs=100, test_all=1,
    savepath='UMLS_Unstructured', datapath='../data/')

# launch(datapath='data/', dataset='umls', fold=0, Nent=184,
#         Nrel=49, loadmodel=False, loademb=False, op='Unstructured',
#         simfn='Dot', ndim=50, nhid=50, marge=1., lremb=0.1, lrparam=1.,
#         nbatches=100, totepochs=2000, test_all=1, seed=666, savepath='.')


print "\n##### EVALUATION #####\n"

ClassifEval(datapath='../data/',
        loadmodel='UMLS_Unstructured/best_valid_model.pkl')
RankingEval(datapath='../data/',
        loadmodel='UMLS_Unstructured/best_valid_model.pkl')
