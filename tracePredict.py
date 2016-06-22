#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs, yaml, math, random, copy
from svmutil import svm_train, svm_predict, svm_read_problem
from grid import *
from tempfile import NamedTemporaryFile
from sklearn import preprocessing
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.datasets import load_svmlight_file
from sklearn.decomposition import PCA

from tracePath import Path


class SvmUtil:
    def __init__(self):
        #load raw traces
        self._traces = []
        self._labels = []

        #get params
        self._tracesSet   = []
        self._tracesLabel = []

        #make sample
        self._trainSet    = []
        self._trainLabel  = []
        self._testSet     = []
        self._testLabel   = []

        #train model
        self._model       = None
        self._param       = None
        pass

    def loadTraces(self, fname):
        y, x = svm_read_problem(fname)
        vectors = []
        for t in x:
            vectors.append( [ v for k, v in t.items() ] )
        self._traces += vectors
        self._labels += y

    def getArray(self, fname):
        vectors, labels = load_svmlight_file(fname)
        return vectors.toarray(), list(labels)

    def getParams(self):
        tmpFile = self.saveTempFile( self._traces, self._labels )

        X, Y = self.getArray(tmpFile.name)

        os.unlink(tmpFile.name)

        X_scaled = preprocessing.scale(X)
        X_pca = PCA().fit_transform(X_scaled)
        
        tmpFile = self.saveTempFile(X_pca, Y)

        _, param = find_parameters(tmpFile.name)
        param_str = '-c ' + str(param['c']) + ' -g ' + str(param['g'])
        
        os.unlink(tmpFile.name)
        
        self._param       = param_str
        self._tracesSet   = X_pca.tolist()
        self._tracesLabel = Y

    def getSample(self):
        self._testSet   = copy.copy( self._tracesSet )
        self._testLabel = copy.copy( self._tracesLabel )

        for i in range( int( len(self._tracesSet)/5) ):
            sampleID = random.sample( range( len(self._testSet) ) ,1 )[0]
            self._trainSet.append( self._testSet[sampleID] )
            self._testSet.remove( self._testSet[sampleID] )
            self._trainLabel.append( self._testLab
            tmpFile.write( string.encode() )
        
        tmpFile.close()
        return tmpFile
    
    def list2vec(self, l):
        s = ''
        for i in range(len(l)):
            s += str(i + 1) + ':' + str(l[i]) + ' '
        return sel[sampleID] )
            self._testLabel.remove( self._testLabel[sampleID] )

    def trainModel(self):
        self._model = svm_train( self._trainLabel , self._trainSet, self._param )

    def getAccuracy(self):
        _, acc, vals = svm_predict( self._testLabel, self._testSet, self._model, '-b 0' )
        return acc, vals

    def saveTempFile(self, traces, labels):
        tmpFile = NamedTemporaryFile(delete=False)

        for i in range(len(traces)):
            string = str(labels[i]) + ' ' + self.list2vec(traces[i]) + '\n' 