#! /usr/bin/python

from myWN_exp import *
from myWN_evaluation import *

#theano.config.compute_test_value = 'warn'

launch(op='GEO', dataset='WN2', simfn='L2', ndim=20, marge=1., lremb=0.01,
    nbatches=100, totepochs=1000, test_all=10, neval=500, savepath='WN2_GEO',
    datapath='../data/', regparam=0.1, Nent=40954, Nsyn=40943, Nrel=11)
# Training takes 4 hours on GTX675M and an intel core i7 processor

#print "\n##### EVALUATION #####\n"

# ClassifEval(datapath='../data/', loadmodel='WN_GEO/best_valid_model_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(ndim, lremb, simfn, regparam)
# myRankingEval(datapath='../data/', loadmodel='WN_GEO/best_valid_model_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(ndim, lremb, simfn, regparam))
