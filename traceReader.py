#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs
import readT3A
from automataElement import AutomataElement, TraceElement, StateElement, EdgeElement

class TraceReader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def getAutomata(self):
        pass

    @abstractmethod
    def getTraces(self):
        pass


class WebTraceReader(TraceReader):
    def __init__(self):
        self.automata     = None
        self.traces       = []
        self.automataJson = None
        self.traceJson    = None

    def loadJson(self, webFolderPath):
        automataPath = os.path.join( webFolderPath, 'automata.json' )
        if not os.path.exists(automataPath):
            raise Exception('Cannot find web automata')

        with open( automataPath, 'r' ) as automataFile:
            self.automataJson = json.load( automataFile )

        tracesPath = os.path.join( webFolderPath, 'traces.json' )
        if not os.path.exists(tracesPath):
            raise Exception('Cannot find web traces')

        with open( tracesPath ) as tracesFile:
            self.traceJson = json.load( tracesFile )

    def parseAutomata(self, webFolderPath):
        self.automata = AutomataElement()
        for state in self.automataJson['state']:
            stateElement = StateElement()
            stateElement.set_id( str( state['id'] ) )
            stateElement.set_xml( 
                os.path.join( webFolderPath, state['dom_path'] ) )
            stateElement.add_keyword( 'url', state['url'] )
            '''TODO load dom and parse keyword'''

            self.automata.add_state( stateElement )

        for edge in self.automataJson['edge']:
            edgeElement = EdgeElement()
            edgeElement.add_keyword( 'id', edge['clickable']['id'] )
            edgeElement.add_keyword( 'name', edge['clickable']['name'] )
            edgeElement.add_keyword( 'xpath', edge['clickable']['xpath'] )
            state_from = str( edge['from'] )
            edgeElement.set_stateFrom( self.automata.get_state_byId( state_from ) )
            state_to   = str( edge['to'] )
            edgeElement.set_stateTo( self.automata.get_state_byId( state_to ) )

            self.automata.add_edge( edgeElement )

    def parseTraces(self, webFolderPath):
        for trace in self.traceJson['traces']:
            traceElement = TraceElement()
            for index, edge in enumerate( trace['edges'] ):
                traceElement.add_edge( 
                    self.automata.get_edge_byFromTo( str(edge['from']), str(edge['to']) ), index )
            for state in trace['states']:
                traceElement.add_state( self.automata.get_state_byId( str(state['id']) ) )
            self.traces.append( traceElement )

    def parseDomLabel(self):
        pass

    def reset(self):
        self.automata     = None
        self.traces       = []
        self.automataJson = None
        self.traceJson    = None

    def getAutomata(self):
        return self.automata

    def getTraces(self):
        return self.traces

class TaaDTraceReader(TraceReader):
    def __init__(self):
        self.automata   = None
        self.traces     = []
        self.taskJson   = None
        self.edgesJson  = None

    def loadJson(self, sessionFile):
        if not ( os.path.exists( sessionFile )                                                or \
                 os.path.exists( os.path.join(sessionFile, 'sessionAutomata') )               or \
                 os.path.exists( os.path.join(sessionFile, 'sessionAutomata', 'edges.json') )      ):
            raise Exception('Cannot find Session Automata')
        if not os.path.exists( os.path.join(sessionFile, 'traceSet') ):
            raise Exception('Cannot find Session traceSet')
        if not os.path.exists( os.path.join(sessionFile, 'task.json') ):
            raise Exception('Cannot find task.json')

        # get session infomation: trace amount
        with open( os.path.join(sessionFile, 'task.json'), 'r') as f:
            self.taskJson = json.load(f)

        # make Automata from session edges.json
        with open( os.path.join(sessionFile, 'sessionAutomata', 'edges.json'), 'r') as f:
            self.edgesJson = json.load(f)

    def parseSessionAutomata(self, sessionFile):
        self.automata = AutomataElement()

        mode = "STATE_TO_EDGE"
        for e in self.edgesJson['edges']:
            if  mode == "STATE_TO_EDGE":
                mode =  "EDGE_TO_STATE"
                stateID = e[0]
                edgeID  = e[1]

                if self.automata.has_stateID(stateID):
                    state = self.automata.get_state_byId(stateID)
                else:
                    state = StateElement()
                    state.set_id( str(stateID) )
                    self.automata.add_state( state )

                if not self.automata.has_edgeID(edgeID) :
                    edge = EdgeElement()
                    edge.set_id( str(edgeID) )
                    edge.set_stateFrom( state )
                    self.automata.add_edge( edge )
                else:
                    edge = self.automata.get_edge_byId(edgeID)
                    if not edge.get_stateFrom():
                        edge.set_stateFrom( state )

            elif mode == "EDGE_TO_STATE":
                mode  =  "STATE_TO_EDGE"
                edgeID  = e[0]
                stateID = e[1]

                if self.automata.has_stateID(stateID):
                    state = self.automata.get_state_byId(stateID)
                else:
                    state = StateElement()
                    state.set_id( str(stateID) )
                    self.automata.add_state( state )

                if not self.automata.has_edgeID(edgeID) :
                    edge = EdgeElement()
                    edge.set_id( str(edgeID) )
                    edge.set_stateTo( state )
                    self.automata.add_edge( edge )
                else:
                    edge = self.automata.get_edge_byId(edgeID)
                    if not edge.get_stateTo():
                        edge.set_stateTo( state )

    def parseTraceSet(self, sessionFile):
        traceAmount = int( taskJson['traceAmount'] )
        for i in range(traceAmount):
            # check TraceSet folder
            traceSetFile = os.path.join(sessionFile, 'traceSet', str(i+1))
            if not os.path.exists( traceSetFile ):
                raise Exception('Cannot find traceSet-',traceSetFile)

            traceTxtFile = os.path.join(sessionFile, 'traceSet', str(i+1), 'trace.txt')
            if not os.path.exists( traceSetFile ):
                raise Exception('Cannot find trace.txt : ',traceTxtFile)

            self.loadTraceSet(traceTxtFile)

    def loadTraceSet(self, traceTxtFile):
        with open(traceTxtFile, 'r') as f:
            traceLines = f.readlines()

        trace = { 'states': [], 'edges': [] }
        mark = '=>'
        for line in traceLines:
            if mark in line:
                words = line.split(mark)
                NodeName = ''.join( words[-1].split() )
                NodeID = NodeName.strip('state')
                NodeFile = ''.join( words[0].split() )

                # check if is state
                if NodeFile.endswith('.xml'):
                    if self.automata.has_stateID(NodeID):
                        state = self.automata.get_state_byId(stateID)
                        state.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['states'].append( se )

                # check if is edge
                elif NodeFile.endswith('.json'):
                    if self.automata.has_edgeID(NodeID):
                        edge = self.automata.get_edge_byId(edgeID)
                        edge.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['edges'].append( ee )
            else:
                break

        # build trace
        traceElement = TraceElement()
        for index, edge in enumerate( trace['edges'] ):
            traceElement.add_edge( edge, index )
        for state in trace['states']:
            traceElement.add_state( state )

        self.traces.append( traceElement )

    def parseT3A(self, T3Afile):
        if not os.path.exists(T3Afile):
            raise Exception("Cannot Find T3A file!")

        t3a = readT3A.read( T3Afile )
        self.loadT3A(t3a)

    def loadT3A(self, t3a):
        #parse Label into automata
        for node in t3a.nodes:
            for stateID in node.stateIDs:
                if stateID in states:
                    states[stateID].add_keyword('label', node.label)
        for branch in t3a.branches:
            if branch.actionIdx in edges:
                edges[ branch.actionIdx ].add_keyword('label', branch.label)

    def reset(self):
        self.automata   = None
        self.traces     = []
        self.taskJson   = None
        self.edgesJson  = None
 
    def getAutomata(self):
        return self.automata

    def getTraces(self):
        return self.traces