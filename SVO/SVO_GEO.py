#! /usr/bin/python

from mySVO_exp import *

#theano.config.compute_test_value = 'warn'

launch(op='GEO', simfn='L2', ndim=20, nhid=20, marge=1., lremb=0.01,
    lrparam=0.01, nbatches=1000, totepochs=500, test_all=1, savepath='SVO_GEO',
    datapath='../data/')
# Training takes 4 hours on GTX675M and an intel core i7 processor

