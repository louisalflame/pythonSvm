#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json

from tracePath import Path
from automataElement import AutomataElement, TraceElement, StateElement, EdgeElement
import readT3A
import TaaDReader

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

    def parseTaaD( self, user=None, App=None, version=None, abstraction=None ):
        if not user:
            raise Exception("TaaD traces need 'user' data!")
        elif not os.path.isdir( os.path.join( Path.TaaD, 'traces', user ) ):
            raise Exception("there's no TaaD user folder")
        elif not App:
            raise Exception("TaaD traces need 'App' data!")
        elif not os.path.isdir( os.path.join( Path.TaaD, 'traces', user, App ) ):
            raise Exception("there's no TaaD App folder")

        AppPath = os.path.join( Path.TaaD, 'traces', user, App )

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

        '''
        if not session:
            for folder in os.listdir( os.path.join( AppPath, version, abstraction ) ):
                if os.path.isdir( os.path.join( AppPath, version, abstraction, folder ) ):
                    sessionPath = os.path.join( AppPath, version, abstraction, folder )
                    self.parseTaaDSession( sessionPath )
        elif not os.path.isdir( os.path.join( AppPath, version, abstraction, session ) ):
            raise Exception("there's no TaaD abstraction folder")
        else:
            sessionPath = os.path.join( AppPath, version, abstraction, session )
            self.parseTaaDSession( sessionPath )
        '''

        #get states, edges, traces from TAAD Session
        sessionPath = os.path.join( AppPath, version, abstraction, 'session1' )
        states, edges, traces = TaaDReader.parseSessionAutomata( sessionPath )

        # get abs\T3A folder, find max number.t3a file
        try:
            num = 1
            while os.path.exists( os.path.join( AppPath, version, abstraction, 'T3A', str(num)+'.t3a' ) ):
                T3Afile = os.path.join( AppPath, version, abstraction, 'T3A', str(num)+'.t3a' )
                num += 1
            if os.path.exists(T3Afile):
                t3a = readT3A.read( T3Afile )
            else:
                raise Exception("Cannot Find T3A file!")
        except Exception as e:
            raise Exception("Cannot load T3A file! \n\n", e)

        #parse Label into automata
        for node in t3a.nodes:
            for stateID in node.stateIDs:
                if stateID in states:
                    states[stateID].add_keyword('label', node.label)
        for branch in t3a.branches:
            if branch.actionIdx in edges:
                edges[ branch.actionIdx ].add_keyword('label', branch.label)


        automataElement = AutomataElement()
        for stateID in states:            
            automataElement.add_state( states[stateID] )
        for edgeID in edges:            
            automataElement.add_edge( edges[edgeID] )
        self.automata = automataElement
 
        for trace in traces:
            traceElement = TraceElement()
            for index, edge in enumerate( trace['edges'] ):
                traceElement.add_edge( edge, index )
            for state in trace['states']:
                traceElement.add_state( state )
            self.traces.append( traceElement )

    def parseWeb( self, foldername=None ):
        # check folder path
        if not foldername:
            raise Exception("B2g traces need 'foldername' data!")
        elif not os.path.isdir( os.path.join( Path.WebCrawler, 'trace', foldername ) ):
            raise Exception("there's no B2g trace folder")
        # check loading json file
        try:
            tracesFile = os.path.join( Path.WebCrawler, 'trace', foldername, 'traces.json' )
            tracesFile = open( tracesFile )
            traces = json.load( tracesFile )
            automataFile = os.path.join( Path.WebCrawler, 'trace', foldername, 'automata.json' )
            automataFile = open( automataFile )
            automata = json.load( automataFile )
        except Exception as e:
            raise e

        # try parse automata json into element class
        automataElement = AutomataElement()
        for state in automata['state']:
            stateElement = StateElement()
            stateElement.set_id( int( state['id'] ) )
            stateElement.set_xml( 
                os.path.join( Path.WebCrawler, 'trace', foldername, state['dom_path'] ) )
            stateElement.add_keyword( 'url', state['url'] )
            '''TODO load dom and parse keyword'''

            automataElement.add_state( stateElement )

        for edge in automata['edge']:
            edgeElement = EdgeElement()
            edgeElement.add_keyword( 'id', edge['clickable']['id'] )
            edgeElement.add_keyword( 'name', edge['clickable']['name'] )
            edgeElement.add_keyword( 'xpath', edge['clickable']['xpath'] )
            state_from = int( edge['from'] )
            edgeElement.set_stateFrom( automataElement.get_state_byId( state_from ) )
            state_to   = int( edge['to'] )
            edgeElement.set_stateTo( automataElement.get_state_byId( state_to ) )

            automataElement.add_edge( edgeElement )
        self.automata = automataElement

        for trace in traces['traces']:
            traceElement = TraceElement()
            for index, edge in enumerate( trace['edges'] ):
                traceElement.add_edge( 
                    automataElement.get_edge_byFromTo( int(edge['from']), int(edge['to']) ), index )
            for state in trace['states']:
                traceElement.add_state( automataElement.get_state_byId( int(state['id']) ) )
            self.traces.append( traceElement )


    def saveTraces(self):
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

        # save traces by automata attributes
        with open( filename, 'w' ) as f:
            for trace in self.traces:
                trace.set_automata( self.automata )
                vector = trace.make_vector_string()
                f.write(vector)
        f.close()

        filename = os.path.join( Path.Data, self.app, self.ver, self.traceName+str(num)+'vector' )
        with open( filename, 'w' ) as f:
            f.write( self.automata.get_vector() )
        f.close()           