#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json

from tracePath import Path
from automataElement import AutomataElement, TraceElement, StateElement, EdgeElement
from traceReader import WebTraceReader, TaaDTraceReader

class ParseUtil:
    def __init__( self, app=None, ver=None ):
        self.app = app
        self.ver = ver
        self.automata = None
        self.traces = []
        self.traceName = "traces"

    def setAppTracesName( self, app , ver ):
        self.app = app
        self.ver = ver

    def getAppName(self):
        return self.app

    def getVersionName(self):
        return self.ver

    def getAppFolder(self):
        return os.path.join( Path.Data, self.app )

    def getTracesFolder(self):
        return os.path.join( Path.Data, self.app, self.traces )

    def resetTraces( self, saveFile=False ):
        if saveFile:
            self.saveTraces()
        self.traces = []

    def parseTaaD( self, user=None, App=None, version=None, abstraction=None, session=None ):
        #check User folder, App folder
        if not user:
            raise Exception("TaaD traces need 'user' data!")
        elif not os.path.isdir( os.path.join( Path.TaaD, 'traces', user ) ):
            raise Exception("there's no TaaD user folder")
        elif not App:
            raise Exception("TaaD traces need 'App' data!")
        elif not os.path.isdir( os.path.join( Path.TaaD, 'traces', user, App ) ):
            raise Exception("there's no TaaD App folder")
        AppPath = os.path.join( Path.TaaD, 'traces', user, App )

        #check Version folder, abstraction folder
        if not version:
            for folder in os.listdir(AppPath):
                if os.path.isdir( os.path.join( AppPath, folder ) ):
                    version = folder
                    break
        elif not os.path.isdir( os.path.join( AppPath, version ) ):
            raise Exception("there's no TaaD version folder")
        if not abstraction:
            for folder in os.listdir( os.path.join( AppPath, version ) ):
                if os.path.isdir( os.path.join( AppPath, version, folder ) ):
                    abstraction = folder
                    break
        elif not os.path.isdir( os.path.join( AppPath, version, abstraction ) ):
            raise Exception("there's no TaaD abstraction folder")
        AbsPath = os.path.join( AppPath, version, abstraction )

        if not session:
            raise Exception("there's no TaaD abstraction folder")
        elif not os.path.isdir( os.path.join( AbsPath, session ) ):
            raise Exception("there's no TaaD abstraction folder")

        sessionPath = os.path.join( AbsPath, session )
        sessionNum = int( session.strip('session') )
        t3aPath = os.path.join( AbsPath, 'T3A', str(sessionNum)+'.t3a' )

        TaaDReader = TaaDTraceReader()
        TaaDReader.loadJson( sessionPath )
        TaaDReader.parseSessionAutomata( sessionPath )
        TaaDReader.parseTraceSet( sessionPath )
        TaaDReader.parseT3A( t3aPath )

        self.automata = TaaDReader.getAutomata()
        self.traces   = TaaDReader.getTraces()
 
    def parseWeb( self, foldername=None ):
        # check folder path
        if not foldername:
            raise Exception("B2g traces need 'foldername' data!")
        elif not os.path.isdir( os.path.join( Path.WebCrawler, 'trace', foldername ) ):
            raise Exception("there's no B2g trace folder")

        webTraceReader = WebTraceReader()

        webFolderPath = os.path.join( Path.WebCrawler, 'trace', foldername )

        webTraceReader.loadJson( webFolderPath )
        webTraceReader.parseAutomata( webFolderPath )
        webTraceReader.parseTraces( webFolderPath )
        webTraceReader.parseDomLabel()

        self.automata = webTraceReader.getAutomata()
        self.traces   = webTraceReader.getTraces()

    def saveTraces(self):
        # make dir if not exist
        if not self.app or not self.ver:
            raise Exception("need set traces's saving app&ver name ")
        if not os.path.isdir( os.path.join( Path.Data, self.app ) ):
            os.makedirs( os.path.join( Path.Data, self.app ) )            
        if not os.path.isdir( os.path.join( Path.Data, self.app, self.ver ) ):
            os.makedirs( os.path.join( Path.Data, self.app, self.ver ) )

        # make filename by num
        num = 1
        while os.path.exists( os.path.join( Path.Data, self.app, self.ver, self.traceName+str(num) ) ):
            num += 1
        filename = os.path.join( Path.Data, self.app, self.ver, self.traceName+str(num) )

        self.automata.use_label_dictionary()
        self.automata.remake_keywords()
        
        # save traces by automata attributes
        with open( filename, 'w' ) as f:
            for trace in self.traces:
                trace.set_automata( self.automata )
                vector = trace.make_vector_string( 'label' )
                f.write(vector)
        f.close()

        filename = os.path.join( Path.Data, self.app, self.ver, self.traceName+str(num)+'vector' )
        with open( filename, 'w' ) as f:
            f.write( self.automata.get_vector( 'label' ) )
        f.close()           