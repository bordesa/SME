#! /usr/bin/python

from Tensor_exp import *
from Tensor_evaluation import *

launch(op='SE', dataset='umls', fold=0, simfn='Dot', Nent=184, Nrel=49, marge=1., lremb=0.01,
    lrparam=0.1, nbatches=100, totepochs=100, test_all=1,
    savepath='UMLS_SE', datapath='../data/')



print "\n##### EVALUATION #####\n"

ClassifEval(datapath='../data/',
        loadmodel='UMLS_SE/best_valid_model.pkl')
RankingEval(datapath='../data/',
        loadmodel='UMLS_SE/best_valid_model.pkl')
