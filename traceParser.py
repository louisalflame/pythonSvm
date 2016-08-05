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
 
    def parseWeb( self, tracefolder=None, foldername=None ):
        # check folder path
        if not tracefolder:
            raise Exception("Web traces need 'tracefolder' data!")
        elif not os.path.isdir( os.path.join( Path.WebCrawler, tracefolder ) ):
            raise Exception("there's no Web trace folder")

        if not foldername:
            raise Exception("Web traces need 'foldername' data!")
        elif not os.path.isdir( os.path.join( Path.WebCrawler, tracefolder, foldername ) ):
            raise Exception("there's no Web trace folder")

        webFolderPath = os.path.join( Path.WebCrawler, tracefolder, foldername )

        webTraceReader = WebTraceReader()
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


#=======================================================================
# USE:
#  1. 建立一個 ParseUtil 的 instance object
#  2. 輸入App和ver的名字，作為parse結果儲存的名稱
#  3. 依據trace的種類使用 parseTaaD() 或 parseWeb()
#     (1)parseTaaD 需要依序輸入 User, APP, version, abstraction, session的名稱
#        才能正確找到trace的路徑
#     (2)parseWeb 需要輸入 tracefolder 和 foldername 名稱
#  4. TaaD 和 WebTraceCollector 檔案位置已記錄在tracePath
#     如有更動，請直接在tracePath.py裡更改
#  5. parse過程會建立 traceReader 的 instance object
#     (1) traceReader 會讀取trace裡的automata
#         並parse每個state和edge
#     (2) traceReader 會讀取traces裡state和edge的順序
#     (3) traceReader 找出state和edge裡的feature
#         在TaaD的trace是找出t3a檔裡的label
#         在Web的trace是從DOM裡找出符合的keyword
#  6. parse完後會儲存parser處理過的automata和traces
#     使用 saveTraces() 將feature儲存為vector的格式
#     (1) self.automata會用 use_label_dictionary() 先建立一個基準的feature vector
#         讀取 SpecElicitor 的 labelDictionary 的所有label
#     (2) 依據此label vector累加trace中每個state和edge的feature
#  7. 如要更改vector的格式:
#     (1) self.automata建立完基準的feature vector後
#         trace 建立一個不同的 make_vector_string() function
#=======================================================================