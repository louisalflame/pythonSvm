#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs, yaml, math, random, copy

#=================================================================
# 需自行安裝LIBSVM https://www.csie.ntu.edu.tw/~cjlin/libsvm/
from svmutil import svm_train, svm_predict, svm_read_problem, evaluations, svm_save_model, svm_load_model
from grid import *
#=================================================================

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
        self._fnames = []
        self._traces = []
        self._labels = []
        self._duplicate = None
        self._duplicateTrain = None

        #make sample
        self._sampleRate  = None
        self._trainSet    = []
        self._trainLabel  = []
        self._testSet     = []
        self._testLabel   = []
        self._trainFail   = {}
        self._testFail    = {}

        #get params
        self._tracesSet   = []
        self._tracesLabel = []

        #train model
        self._model       = None
        self._param       = None

        #record traces origin
        self._records      = []
        self._sample       = []

        #SVM result
        self._accuracy     = None
        self._predictLabel = []

        #result analysis
        self._precision = None 
        self._recall    = None
        self.TP_traces = {}
        self.FP_traces = {}
        self.FN_traces = {}

    #可以load的file需經過ParseUtil處理過成svm_read_problem可以使用的格式
    def loadTraces(self, fname, reLoad=False):
        if not reLoad:
            self._fnames.append(fname)

        y, x = svm_read_problem(fname)
        vectors = []
        record = []
        for t, i in zip( x, range(len(x)) ):
            vectors.append( [ v for k, v in t.items() ] )
            record.append( str(fname)+'_'+str(i) )

        self._traces += vectors
        self._labels += y
        self._records += record

    def preprocessing(self):
        tmpFile = self.saveTempFile( self._traces, self._labels )

        X, Y = self.getArray(tmpFile.name)

        os.unlink(tmpFile.name)

        X_scaled = preprocessing.scale(X)
        X_pca = PCA().fit_transform(X_scaled)
        
        self._tracesSet   = X_pca.tolist()
        self._tracesLabel = Y

    def duplicate(self, num):
        self._duplicate = num
        traces = []
        labels = []
        record = []
        for i in range(num):
            traces += copy.copy( self._tracesSet )
            labels += copy.copy( self._tracesLabel )
            record += copy.copy( self._records )
        self._tracesSet   = traces
        self._tracesLabel = labels
        self._records     = record

        return len(self._tracesSet), len(self._tracesLabel)

    def getRandomSample(self, rate):
        self._sampleRate = rate
        records = [ [],[] ]
        for trace, label, r, i in zip( self._tracesSet, self._tracesLabel, self._records, range(len(self._records)) ):
            if random.random() < rate:
                self._sample.append(1)
                records[0].append(r)
                self._trainSet.append( copy.copy( trace ) )
                self._trainLabel.append( copy.copy( label ) )
                if label == 1:
                    if r in self._trainFail:
                        self._trainFail[r] += 1
                    else:
                        self._trainFail[r] = 1
            else:
                self._sample.append(2)
                records[1].append(r)
                self._testSet.append( copy.copy( trace ) )
                self._testLabel.append( copy.copy( label ) )
                if label == 1:
                    if r in self._testFail:
                        self._testFail[r] += 1
                    else:
                        self._testFail[r] = 1

        self._records = records
        return len(self._trainSet), len(self._trainLabel), len(self._testSet), len(self._testLabel)

    def duplicateTrain(self, num):
        self._duplicateTrain = num
        traces = []
        labels = []
        record = []
        for i in range(num):
            traces += copy.copy( self._trainSet )
            labels += copy.copy( self._trainLabel )
            record += copy.copy( self._records[0] )
        self._trainSet   = traces
        self._trainLabel = labels
        self._records[0] = record

        return len(self._trainSet), len(self._trainLabel)

    # find_parameter 是LIBSVM中的grid.py的function
    def getParams(self):
        sys.stdout = open(os.devnull, "w")

        tmpFile = self.saveTempFile( self._trainSet, self._trainLabel )

        _, param = find_parameters(tmpFile.name)
        param_str = '-c ' + str(param['c']) + ' -g ' + str(param['g'])+' -b 1'
        
        os.unlink(tmpFile.name)

        sys.stdout = sys.__stdout__
        self._param = param_str

    def trainModel(self):
        sys.stdout = open(os.devnull, "w")

        self._model = svm_train( self._trainLabel , self._trainSet, self._param )
        
        sys.stdout = sys.__stdout__

    def getAccuracy(self):
        labs, acc, vals = svm_predict( self._testLabel, self._testSet, self._model )
        self._predictLabel = labs
        self._accuracy = acc

    def evaluations(self):
        ACC, MSE, SCC = evaluations(self._testLabel, self._predicts)
        self._accuracy = ACC

    def countPrecisionRecall(self):
        true_positive = []
        false_positive = []
        false_negative = []
        for p, l, i in zip( self._predictLabel, self._testLabel, self._records[1] ):
            if p == l and p == 1:
                true_positive.append(i)
            elif p != l and p == 1:
                false_positive.append(i)
            elif p != l and p == 0:
                false_negative.append(i)

        self._TP = true_positive
        self._FP = false_positive
        self._FN = false_negative

        self._precision = len(self._TP) / ( len(self._TP)+len(self._FP) ) if len(self._TP)+len(self._FP) > 0 else None
        self._recall    = len(self._TP) / ( len(self._TP)+len(self._FN) ) if len(self._TP)+len(self._FN) > 0 else None

        return  { 'precision': self._precision,  'recall' : self._recall  }

    def collectRecords(self):
        testNum = 0
        for r in self._TP:
            if r in self.TP_traces:
                self.TP_traces[r] += 1
            else:
                self.TP_traces[r] = 1
        for r in self._FP:
            if r in self.FP_traces:
                self.FP_traces[r] += 1
            else:
                self.FP_traces[r] = 1
        for r in self._FN:
            if r in self.FN_traces:
                self.FN_traces[r] += 1
            else:
                self.FN_traces[r] = 1

    def prettyPrint(self, full=True ):
        strings = []
        strings.append( "Filenames: "+ ', '.join(self._fnames) )
        strings.append( "Duplicate: *="+ str( self._duplicate ) )
        strings.append( "Duplicate: Train *="+ str( self._duplicateTrain ) )
        strings.append( "Random   : "+str(self._sampleRate) )
        strings.append( "Training : "+str(len(self._trainSet)) )
        strings.append( "Testing  : "+str(len(self._testSet)) )
        strings.append( "Params   : "+str(self._param) )
        strings.append( "Accuracy : "+str(self._accuracy) )
        strings.append( "Precision: "+str(self._precision) )
        strings.append( "Recall   : "+str(self._recall) )
        if full:
            strings.append( "Failtrain: "+str(self._trainFail) )
            strings.append( "Failtest : "+str(self._testFail) )
            strings.append( "TP_traces: "+str(self.TP_traces) )
            strings.append( "FP_traces: "+str(self.FP_traces) )
            strings.append( "FN_traces: "+str(self.FN_traces) )
        print ( "\n".join(strings) )

    def reset(self):
        self._traces         = []
        self._labels         = []
        self._duplicate      = None
        self._duplicateTrain = None
        self._sampleRate     = None
        self._tracesSet      = []
        self._tracesLabel    = []
        self._trainSet       = []
        self._trainLabel     = []
        self._testSet        = []
        self._testLabel      = []
        self._trainFail      = {}
        self._testFail       = {}
        self._model          = None
        self._param          = None
        self._records        = []
        self._sample         = []
        self._accuracy       = None
        self._predictLabel   = []
        self._precision      = None 
        self._recall         = None
        self.TP_traces       = {}
        self.FP_traces       = {}
        self.FN_traces       = {}

#========================================================================================================
# usility functions
#========================================================================================================
    def getArray(self, fname):
        vectors, labels = load_svmlight_file(fname)
        return vectors.toarray(), list(labels)

    def saveTempFile(self, traces, labels):
        tmpFile = NamedTemporaryFile(delete=False)

        for i in range(len(traces)):
            string = str(labels[i]) + ' ' + self.list2vec(traces[i]) + '\n' 
            tmpFile.write( string.encode() )
            tmpFile.flush()

        tmpFile.close()
        return tmpFile

    def list2vec(self, l):
        s = ''
        for i in range(len(l)):
            s += str(i + 1) + ':' + str(l[i]) + ' '
        return s

    def saveModel(self, fname):
        svm_save_model( fname, self._model )

#========================================================================================================
# 簡易重複執行的script
#========================================================================================================
    def simpleRun(self, duplicate=1, sampleRaterate=0.5 , duplicateTrain=1 ):
        self.preprocessing()

        self.duplicate( duplicate )
        self.getRandomSample(sampleRaterate)
        self.duplicateTrain( duplicateTrain )

        self.getParams()
        self.trainModel()
        self.getAccuracy()
        self.countPrecisionRecall()
        self.collectRecords()
        self.prettyPrint()

    def reload(self):
        for fname in self._fnames:
            self.loadTraces(fname, True)
