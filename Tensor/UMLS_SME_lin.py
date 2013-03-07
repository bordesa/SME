#! /usr/bin/python

from Tensor_exp import *
from Tensor_evaluation import *

launch(op='SME_lin', dataset='umls', fold=0, simfn='Dot', Nent=184, Nrel=49, marge=1., lremb=0.01,
    lrparam=0.1, nbatches=100, totepochs=100, test_all=10,
    savepath='UMLS_SME_lin', datapath='../data/')



print "\n##### EVALUATION #####\n"

ClassifEval(datapath='../data/',
        loadmodel='UMLS_SME_lin/best_valid_model.pkl')
RankingEval(datapath='../data/',
        loadmodel='UMLS_SME_lin/best_valid_model.pkl')
