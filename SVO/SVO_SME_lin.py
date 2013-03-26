#! /usr/bin/python

from SVO_exp import *

#theano.config.compute_test_value = 'warn'

launch(op='SME_lin', simfn='Dot', ndim=50, nhid=50, marge=1., lremb=0.001,
    lrparam=0.01, nbatches=100, totepochs=500, test_all=1, savepath='SVO_SME_lin',
    datapath='../data/', regparam=0.1, neval=500)
# Training takes 4 hours on GTX675M and an intel core i7 processor

