#! /usr/bin/python

from myTensor_exp import *

launch(op='SE2', dataset='kinships', fold=0, simfn='L1', Nent=130, Nrel=26, marge=1., lremb=0.01,
    lrparam=0.1, nbatches=100, totepochs=100, test_all=10,
    savepath='Kinships_SE', datapath='../data/')



print "\n##### EVALUATION #####\n"

ClassifEval(datapath='../data/',
        loadmodel='UMLS_SE/best_valid_model.pkl')
RankingEval(datapath='../data/',
        loadmodel='UMLS_SE/best_valid_model.pkl')
