#! /usr/bin/python

from myTensor_exp import *


launch(op='GEO2', dataset='kinships', fold=0, simfn='L2', ndim=50, marge=1., lremb=0.001,
    nbatches=100, totepochs=5000, test_all=10, savepath='kinships_GEO2',
    datapath='../data/', regparam=0.0, Nent=130, Nrel=26)


