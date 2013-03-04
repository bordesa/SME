#! /usr/bin/python

from mySVO_exp import *
from mySVO_evaluation import *

#theano.config.compute_test_value = 'warn'

launch(op='GEO', simfn='L1', ndim=20, nhid=20, marge=1., lremb=0.1,
    lrparam=0.1, nbatches=1000, totepochs=500, test_all=1, savepath='SVO_GEO',
    datapath='../data/')
# Training takes 4 hours on GTX675M and an intel core i7 processor

print "\n##### EVALUATION #####\n"

#ClassifEval(datapath='../data/', loadmodel='WN_GEO/best_valid_model.pkl')
myRankingEval(datapath='../data/', loadmodel='SVO_GEO/best_valid_model.pkl')
