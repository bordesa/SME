#! /usr/bin/python

from myTensor_exp import *


launch(op='GEO', dataset='umls', fold=0, simfn='L2', ndim=20, marge=1., lremb=0.01,
    nbatches=100, totepochs=100, test_all=10, savepath='umls_GEO',
    datapath='../data/', regparam=0.1, Nent=184, Nrel=49)


