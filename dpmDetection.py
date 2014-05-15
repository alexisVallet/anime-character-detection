import cv2
import pymatlab as mlb

class DPMObjectDetection:
    def __init__(self):
        self.session = mlb.session_factory()
        self.session.run('cd ./voc-dpm/')
        self.model = None

        def trainDPMmodel(self, model, pos, neg, warp, randneg, nbiter, nbnegiter, 
                          maxnumexamples, overlap, numfp, cont, tag, C):
            """ Trains a model opptimizing a WL-SSVM or LSVM. 
            (thin wrapper around matlab code by Girshick, R. B.)
            Returns:
            model     The new model

            Arguments
            warp      1 => use warped positives
                      0 => use latent positives
            randneg   1 => use random negaties
                      0 => use hard negatives
            iter      The number of training iterations
            negiter   The number of data-mining steps within each training iteration
            max_num_examples  
                      The maximum number of negative examples that the feature vector
                      cache may hold
            overlap   The minimum overlap in latent positive search
            cont      True => restart training from a previous run
            C         Regularization/surrogate loss tradeoff parameter
            """
            self.session.run('cd ./train/')
            self.session.putvalue('model', model)
            self.session.putvalue('pos', pos)
            self.session.putvalue('neg', neg)
            self.session.putvalue('warp', warp)
            self.session.putvalue('randneg', randneg)
            self.session.putvalue('iter', nbiter)
            self.session.putvalue('negiter', nbnegiter)
            self.session.putvalue('maximum_examples', maximumexamples)
            self.session.putvalue('overlap', overlap)
            self.session.putvalue('num_fp', numfp)
            self.session.putvalue('cont', cont)
            self.session.putvalue('tag', tag)
            self.session.putvalue('C', C)
            self.session.run('nmodel = train(model,pos,neg.warp,randneg,iter,negiter,max_num_exampples,overlap,num_fp,cont,tag,C)')
            self.model = self.session.getvalue('nmodel')
            self.session.run('cd ../')

        def detectObject(image, thresh, max_num):
            if self.model == None:
                
            self.session.run('cd ./features/')
            self.session.putvalue('im', image)
            self.session.putvalue('model', self.model)
            
