#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

from tracePath import Path

class ParseUtil:
    def __init__( self, app=None, ver=None ):
        self.app = app
        self.ver = ver
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

    def parseTaaDSession( self, sessionPath ):
        for f in os.listdir( os.path.join( sessionPath, 'traceSet' ) ):
            pass

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
                vertor = trace.make_vector_string()
                f.write(vector+'\n')
        f.close()

    def parseB2g( self, foldername=None ):
        # check folder path
        if not foldername:
            raise Exception("B2g traces need 'foldername' data!")
        elif not os.path.isdir( os.path.join( Path.B2gBrowser, 'trace', foldername ) ):
            raise Exception("there's no B2g trace folder")
        # check loading json file
        try:
            tracesFile = os.path.join( Path.B2gBrowser, 'trace', foldername, 'traces.json' )
            tracesFile = open( tracesFile )
            traces = json.load( tracesFile )
            automataFile = os.path.join( Path.B2gBrowser, 'trace', foldername, 'automata.json' )
            automataFile = open( automataFile )
            automata = json.load( automataFile )
        except Exception as e:
            raise e

        # try parse automata json into element class
        automataElement = AutomataElement()
        for state in automata['state']:
            stateElement = StateElement()
            stateElement.set_id( int( state['id'] ) )
            stateElement.add_keyword( 'url', state['url'] )
            '''TODO load dom and parse keyword'''

            automataElement.add_state( stateElement )

        for edge in automata['edge']:
            edgeElement = EdgeElement()
            edgeElement.set_id( edge['clickable']['id'] )
            edgeElement.set_name( edge['clickable']['name'] )
            edgeElement.set_Xpath( edge['clickable']['xpath'] )
            state_from = int( edge['from'] )
            edgeElement.set_stateFrom( automataElement.get_state_byId( state_from ) )
            state_to   = int( edge['to'] )
            edgeElement.set_stateTo( automataElement.get_state_byId( state_to ) )

            automataElement.add_edge( edgeElement )
        self.automata = automataElement

        for trace in traces['traces']:
            traceElement = TraceElement()
            for edge in trace['edges']:
                traceElement.add_edge( automataElement.get_edge_byFromTo( 
                    int(edge['from']), int(edge['to']) ) )
            for state in trace['states']:
                traceElement.add_state( automataElement.get_state_byId( int(state['id']) ) )
            self.traces.append( traceElement )


class AutomataElement:
    def __init__(self):
        # basic
        self.edges = []
        self.states = []
        # vector
        self.keywords = {}
        self.actions = {}
        self.orders = {}

    def add_state(self, state):
        if state not in self.states:
            self.states.append( state )
            for key, keyword in state.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = [ keyword ]
                else:
                    self.keywords[key].append( keyword )

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append( edge )
            # add actions
            self.actions[]

    def get_state_byId(self, id):
        for state in self.states:
            if state.get_id() == id:
                return state
        return None

    def get_edge_byFromTo(self, stateFrom, stateTo):
        for edge in self.edges:
            if edge.get_stateFrom().get_id() == stateFrom and \
               edge.get_stateTo().get_id()   == stateTo:
                return edge
        return None

    def make_attribute(self):
        return {}

class TraceElement:
    def __init__(self):
        # basic
        self.states = []
        self.edges = []
        # vector
        self.keywords = {}
        self.actions = {}
        self.orders = {}
        # automata
        self.automata = None

    def add_state(self, state):
        self.states.append( state )

    def add_edge(self, edge):
        self.edges.append(edge)

    def set_automata(self, automata):
        self.automata = automata

    def make_vector_string(self):
        vector = []
        vectorStr = ""
        # add keywords
        # add actions
        # add orders
        vector = [ str(index+1)+':'+str(value) for index, value in enumerate(vector) ]
        vectorStr = ' '.join(vector) + '\n'
        return vectorStr

class StateElement:
    def __init__(self):
        self.id = None
        self.xml = None
        self.keywords = {}

    def add_keyword(self, key, keyword):
        if key not in self.keywords:
            self.keywords[key] = keyword

    def get_keywords(self):
        return self.keywords

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

class EdgeElement:
    def __init__(self):
        self.id        = None
        self.name      = None
        self.xpath     = None
        self.attr      = {}
        self.stateFrom = None
        self.StateTo   = None

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_Xpath(self, xpath):
        self.xpath = xpath

    def set_stateFrom(self, stateFrom):
        self.stateFrom = stateFrom

    def set_stateTo(self, stateTo):
        self.stateTo = stateTo

    def get_stateFrom(self):
        return self.stateFrom

    def get_stateTo(self):
        return self.stateTo