#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs
try:
   import cPickle as pickle
except:
   import pickle

from tracePath import Path

sys.path.append( os.path.join( Path.TaaD, 'src' ) )
import util

def read( filename ):
    with open( filename, "rb" ) as objFile:
        t3a = pickle.load(objFile)
    return t3a
