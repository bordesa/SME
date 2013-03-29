#! /usr/bin/python

from mySVO_exp import *

#theano.config.compute_test_value = 'warn'

launch(op='GEO', simfn='L2', ndim=20, nhid=20, marge=1., lremb=0.01,
    lrparam=0.01, nbatches=100, totepochs=500, test_all=10, savepath='SVO_GEO',
    datapath='../data/', regparam=0.1, neval=500)
# Training takes 4 hours on GTX675M and an intel core i7 processor

