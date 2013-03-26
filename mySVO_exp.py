#! /usr/bin/python

from mymodel import *


# Utils ----------------------------------------------------------------------
def create_random_mat(shape, listidx=None):
    """
    This function create a random sparse index matrix with a given shape. It
    is useful to create negative triplets.

    :param shape: shape of the desired sparse matrix.
    :param listidx: list of index to sample from (default None: it samples from
                    all shape[0] indexes).

    :note: if shape[1] > shape[0], it loops over the shape[0] indexes.
    """
    if listidx is None:
        listidx = np.arange(shape[0])
    listidx = listidx[np.random.permutation(len(listidx))]
    randommat = scipy.sparse.lil_matrix((shape[0], shape[1]),
            dtype=theano.config.floatX)
    idx_term = 0
    for idx_ex in range(shape[1]):
        if idx_term == len(listidx):
            idx_term = 0
        randommat[listidx[idx_term], idx_ex] = 1
        idx_term += 1
    return randommat.tocsr()


def load_file(path):
    return scipy.sparse.csr_matrix(cPickle.load(open(path)),
            dtype=theano.config.floatX)


def convert2idx(spmat):
    rows, cols = spmat.nonzero()
    return rows[np.argsort(cols)]


class DD(dict):
    """This class is only used to replace a state variable of Jobman"""

    def __getattr__(self, attr):
        if attr == '__getstate__':
            return super(DD, self).__getstate__
        elif attr == '__setstate__':
            return super(DD, self).__setstate__
        elif attr == '__slots__':
            return super(DD, self).__slots__
        return self[attr]

    def __setattr__(self, attr, value):
        assert attr not in ('__getstate__', '__setstate__', '__slots__')
        self[attr] = value

    def __str__(self):
        return 'DD%s' % dict(self)

    def __repr__(self):
        return str(self)

    def __deepcopy__(self, memo):
        z = DD()
        for k, kv in self.iteritems():
            z[k] = copy.deepcopy(kv, memo)
        return z

# ----------------------------------------------------------------------------


# Experiment function --------------------------------------------------------
def SVOexp(state, channel):

    # Show experiment parameters
    print >> sys.stderr, state
    np.random.seed(state.seed)

    # Experiment folder
    if hasattr(channel, 'remote_path'):
        state.savepath = channel.remote_path + '/'
    elif hasattr(channel, 'path'):
        state.savepath = channel.path + '/'
    else:
        if not os.path.isdir(state.savepath):
            os.mkdir(state.savepath)

    # Positives
    trainl = load_file(state.datapath + state.dataset + '-train-lhs.pkl')
    trainr = load_file(state.datapath + state.dataset + '-train-rhs.pkl')
    traino = load_file(state.datapath + state.dataset + '-train-rel.pkl')
    if state.op == 'SE' or state.op == 'GEO':
        traino = traino[-state.Nrel:, :]


    # Valid set
    validl = load_file(state.datapath + state.dataset + '-valid-lhs.pkl')
    validr = load_file(state.datapath + state.dataset + '-valid-rhs.pkl')
    valido = load_file(state.datapath + state.dataset + '-valid-rel.pkl')
    if state.op == 'SE'or state.op == 'GEO':
        valido = valido[-state.Nrel:, :]

    # Test set
    testl = load_file(state.datapath + state.dataset + '-test-lhs.pkl')
    testr = load_file(state.datapath + state.dataset + '-test-rhs.pkl')
    testo = load_file(state.datapath + state.dataset + '-test-rel.pkl')
    if state.op == 'SE'or state.op == 'GEO':
        testo = testo[-state.Nrel:, :]

    # Index conversion
    trainlidx = convert2idx(trainl)[:state.neval]
    trainridx = convert2idx(trainr)[:state.neval]
    trainoidx = convert2idx(traino)[:state.neval]
    validlidx = convert2idx(validl)[:state.neval]
    validridx = convert2idx(validr)[:state.neval]
    validoidx = convert2idx(valido)[:state.neval]
    testlidx = convert2idx(testl)[:state.neval]
    testridx = convert2idx(testr)[:state.neval]
    testoidx = convert2idx(testo)[:state.neval]

    # Model declaration
    if not state.loadmodel:
        # operators
        if state.op == 'Unstructured':
            leftop = Unstructured()
            rightop = Unstructured()
        elif state.op == 'SME_lin':
            leftop = LayerLinear(np.random, 'lin', state.ndim, state.ndim,
                    state.nhid, 'left')
            rightop = LayerLinear(np.random, 'lin', state.ndim, state.ndim,
                    state.nhid, 'right')
        elif state.op == 'SME_bil':
            leftop = LayerBilinear(np.random, 'lin', state.ndim, state.ndim,
                    state.nhid, 'left')
            rightop = LayerBilinear(np.random, 'lin', state.ndim, state.ndim,
                    state.nhid, 'right')
        elif state.op == 'SE':
            leftop = LayerMat('lin', state.ndim, state.nhid)
            rightop = LayerMat('lin', state.ndim, state.nhid)
        elif state.op == 'GEO':
            leftop = LayerdMat()
            rightop = Unstructured()
        # embeddings
        if not state.loademb:
            embeddings = Embeddings(np.random, state.Nent, state.ndim, 'emb')
        else:
            f = open(state.loademb)
            embeddings = cPickle.load(f)
            f.close()
        if state.op == 'SE' and type(embeddings) is not list:
            relationl = Embeddings(np.random, state.Nrel,
                    state.ndim * state.nhid, 'rell')
            relationr = Embeddings(np.random, state.Nrel,
                    state.ndim * state.nhid, 'relr')
            embeddings = [embeddings, relationl, relationr]
        if state.op == 'GEO' and type(embeddings) is not list:
            relationMat = Embeddings(np.random, state.Nrel,
                    state.ndim, 'relmat')
            relationVec = Embeddings(np.random, state.Nrel,
                    state.ndim, 'relvec')
            embeddings = [embeddings, relationMat, relationVec]
        simfn = eval(state.simfn + 'sim')
    else:
        f = open(state.loadmodel)
        embeddings = cPickle.load(f)
        leftop = cPickle.load(f)
        rightop = cPickle.load(f)
        simfn = cPickle.load(f)
        f.close()

    # Function compilation
#    trainfunc = myTrainFn1Member_relonly(simfn, embeddings, leftop, rightop,
#            marge=state.marge, regparam=state.regparam)
#    rankrelfunc = myRankRelFnIdx(simfn, embeddings, leftop, rightop)

    trainfunc = myTrainFn1Member(simfn, embeddings, leftop, rightop,
            marge=state.marge, rel=True, regparam=state.regparam)
    # ranklfunc = myRankLeftFnIdx(simfn, embeddings, leftop, rightop,
    #         subtensorspec=state.Nsyn)
    # rankrfunc = myRankRightFnIdx(simfn, embeddings, leftop, rightop,
    #         subtensorspec=state.Nsyn)

    rankrelfunc = myRankRelFnIdx(simfn, embeddings, leftop, rightop)


    out = []
    outb = []
    state.bestvalid = -1

    batchsize = trainl.shape[1] / state.nbatches

    print >> sys.stderr, "BEGIN TRAINING"
    timeref = time.time()
    for epoch_count in xrange(1, state.totepochs + 1):
        # Shuffling
        order = np.random.permutation(trainl.shape[1])
        trainl = trainl[:, order]
        trainr = trainr[:, order]
        traino = traino[:, order]

        # Negatives
        trainln = create_random_mat(trainl.shape, np.arange(state.Nsyn))
        trainrn = create_random_mat(trainr.shape, np.arange(state.Nsyn))
        trainon = create_random_mat(traino.shape, np.arange(state.Nrel))


        #trainln = trainln[:, np.random.permutation(trainln.shape[1])]
        #trainrn = trainrn[:, np.random.permutation(trainrn.shape[1])]

        for i in range(state.nbatches):
            tmpl = trainl[:, i * batchsize:(i + 1) * batchsize]
            tmpr = trainr[:, i * batchsize:(i + 1) * batchsize]
            tmpo = traino[:, i * batchsize:(i + 1) * batchsize]
            tmpnl = trainln[:, i * batchsize:(i + 1) * batchsize]
            tmpnr = trainrn[:, i * batchsize:(i + 1) * batchsize]
            tmpno = trainon[:, i * batchsize:(i + 1) * batchsize]


            # training iteration
            outtmp = trainfunc(state.lremb, state.lrparam / float(batchsize),
                    tmpl, tmpr, tmpo, tmpnl, tmpnr, tmpno)
            out += [outtmp[0] / float(batchsize)]
            outb += [outtmp[1]]
            # embeddings normalization
            if type(embeddings) is list:
                embeddings[0].normalize()
            else:
                embeddings.normalize()

        if (epoch_count % state.test_all) == 0:
            # model evaluation
            print >> sys.stderr, "-- EPOCH %s (%s seconds per epoch):" % (
                    epoch_count,
                    round(time.time() - timeref, 3) / float(state.test_all))
            timeref = time.time()
            print >> sys.stderr, "COST >> %s +/- %s, %% updates: %s%%" % (
                    round(np.mean(out), 4), round(np.std(out), 4),
                    round(np.mean(outb) * 100, 3))
            out = []
            outb = []
#            resvalid = RankingScoreIdx(ranklfunc, rankrfunc, validlidx, validridx, validoidx)
#            state.valid = np.mean(resvalid[0] + resvalid[1])
            resvalid = myRankingScoreRelIdx(rankrelfunc, validlidx, validridx, validoidx)
            state.valid = np.mean(resvalid)

            # restrain = RankingScoreIdx(ranklfunc, rankrfunc,trainlidx, trainridx, trainoidx)
            # state.train = np.mean(restrain[0] + restrain[1])
            restrain = myRankingScoreRelIdx(rankrelfunc, trainlidx, trainridx, trainoidx)
            state.train = np.mean(restrain)

            print >> sys.stderr, "\tMEAN RANK >> valid: %s, train: %s" % (
                    state.valid, state.train)
            if state.bestvalid == -1 or state.valid < state.bestvalid:
#                restest = RankingScoreIdx(ranklfunc, rankrfunc, testlidx, testridx, testoidx)
#                state.besttest = np.mean(restest[0] + restest[1])
                restest = myRankingScoreRelIdx(rankrelfunc, testlidx, testridx, testoidx)
                state.besttest = np.mean(restest)
                state.bestvalid = state.valid
                state.besttrain = state.train
                state.bestepoch = epoch_count
                # Save model best valid model
                f = open(state.savepath + '/best_valid_model_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(state.ndim, state.lremb, state.simfn, state.regparam), 'w')
                cPickle.dump(embeddings, f, -1)
                cPickle.dump(leftop, f, -1)
                cPickle.dump(rightop, f, -1)
                cPickle.dump(simfn, f, -1)
                f.close()
                print >> sys.stderr, "\t\t##### NEW BEST VALID >> test: %s" % (
                        state.besttest)
            # Save current model
            f = open(state.savepath + '/current_model_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(state.ndim, state.lremb, state.simfn, state.regparam), 'w')
            cPickle.dump(embeddings, f, -1)
            cPickle.dump(leftop, f, -1)
            cPickle.dump(rightop, f, -1)
            cPickle.dump(simfn, f, -1)
            f.close()
            state.nbepochs = epoch_count
            print >> sys.stderr, "\t(the evaluation took %s seconds)" % (
                round(time.time() - timeref, 3))
            timeref = time.time()
            channel.save()
    return channel.COMPLETE


def launch(datapath='data/', dataset='SVO', Nent=35152,
        Nsyn=30605, Nrel=4547, loadmodel=False, loademb=False, op='Unstructured',
        simfn='Dot', ndim=50, nhid=50, marge=1., lremb=0.1, lrparam=1.,
        nbatches=100, totepochs=2000, test_all=1, neval=500, seed=666,
        savepath='.', regparam=0.0):

    # Argument of the experiment script
    state = DD()

    state.datapath = datapath
    state.dataset = dataset
    state.Nent = Nent
    state.Nsyn = Nsyn
    state.Nrel = Nrel
    state.loadmodel = loadmodel
    state.loademb = loademb
    state.op = op
    state.simfn = simfn
    state.ndim = ndim
    state.nhid = nhid
    state.marge = marge
    state.lremb = lremb
    state.lrparam = lrparam
    state.nbatches = nbatches
    state.totepochs = totepochs
    state.test_all = test_all
    state.neval = neval
    state.seed = seed
    state.savepath = savepath
    state.regparam = regparam

    if not os.path.isdir(state.savepath):
        os.mkdir(state.savepath)

    # Jobman channel remplacement
    class Channel(object):
        def __init__(self, state):
            self.state = state
            f = open(self.state.savepath + '/orig_state_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(state.ndim, state.lremb, state.simfn, state.regparam), 'w')
            cPickle.dump(self.state, f, -1)
            f.close()
            self.COMPLETE = 1

        def save(self):
            f = open(self.state.savepath + '/current_state_nhid={}_lr={}_simfn={}_reg={}.pkl'.format(state.ndim, state.lremb, state.simfn, state.regparam), 'w')
            cPickle.dump(self.state, f, -1)
            f.close()

    channel = Channel(state)

    SVOexp(state, channel)

if __name__ == '__main__':
    launch()
