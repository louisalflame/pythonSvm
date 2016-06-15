#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs
from abc import ABCMeta, abstractmethod

import readT3A
from automataElement import AutomataElement, TraceElement, StateElement, EdgeElement
from labelDictionary import LabelDictionary

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
                os.path.abspath( os.path.join( webFolderPath, state['dom_path'] ) ) )
            stateElement.add_keyword( 'url', state['url'] )
            '''TODO load dom and parse keyword'''

            self.automata.add_state( stateElement )

        for edge in self.automataJson['edge']:
            edgeElement = EdgeElement()
            edgeElement.set_id( str( edge['id'] ) )
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
                traceElement.add_edge( self.automata.get_edge_byId( str(edge['id']) ), index )
            for state in trace['states']:
                traceElement.add_state( self.automata.get_state_byId( str(state['id']) ) )
            self.traces.append( traceElement )

    def parseDomLabel(self):
        LabelDictionary.parseLabel()
        labelDiction = LabelDictionary.getLabelDictionary()

        for state in self.automata.get_states():
            dom = self.getStateDom( state.get_xml() )

            for label_key, labels in labelDiction['screen'].items():
                for label in labels:
                    if label in dom:
                        state.add_keyword('label', label_key)

        for edge in self.automata.get_edges():
            symbol = edge.get_symbol()

            for label_key, labels in labelDiction['action'].items():
                for label in labels:
                    if label in symbol:
                        edge.add_keyword('label', label_key)

    def getStateDom(self, baseDomFile):
        dom = ""

        if os.path.exists(baseDomFile):
            baseDom = codecs.open(baseDomFile, 'r', encoding='utf-8')
            dom = baseDom.read()

        listJsonPath = os.path.join( baseDomFile, os.pardir, 'iframe_list.json' )
        if os.path.exists( listJsonPath ):
            listJsonFile = open( listJsonPath, 'r' )
            listJson = json.load( listJsonFile )

            if listJson['num'] and int( listJson['num'] ) > 0:
                for i in range( int( listJson['num'] ) ):
                    dom_path = os.path.join( baseDomFile, os.pardir, str(i+1), os.path.basename(baseDomFile) )
                    if os.path.exists(dom_path):
                        iframedom = codecs.open(baseDomFile, 'r', encoding='utf-8')
                        dom += iframedom.read()

        return dom

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
        statesList = {}
        edgesList = {}

        mode = "STATE_TO_EDGE"
        for e in self.edgesJson['edges']:
            if  mode == "STATE_TO_EDGE":
                mode =  "EDGE_TO_STATE"
                stateID = e[0]
                edgeID  = e[1]

                if stateID in statesList:
                    state = statesList[stateID]
                else:
                    state = StateElement()
                    state.set_id( str(stateID) )
                    statesList[stateID] = state

                if edgeID not in edgesList:
                    edge = EdgeElement()
                    edge.set_id( str(edgeID) )
                    edge.set_stateFrom( state )
                    edgesList[edgeID] = edge
                else:
                    edge = edgesList[edgeID]
                    if not edge.get_stateFrom():
                        edge.set_stateFrom( state )

            elif mode == "EDGE_TO_STATE":
                mode  =  "STATE_TO_EDGE"
                edgeID  = e[0]
                stateID = e[1]

                if stateID in statesList:
                    state = statesList[stateID]
                else:
                    state = StateElement()
                    state.set_id( str(stateID) )
                    statesList[stateID] = state

                if edgeID not in edgesList:
                    edge = EdgeElement()
                    edge.set_id( str(edgeID) )
                    edge.set_stateTo( state )
                    edgesList[edgeID] = edge
                else:
                    edge = edgesList[edgeID]
                    if not edge.get_stateTo():
                        edge.set_stateTo( state )

        self.automata = AutomataElement()
        for stateID, state in statesList.items():
            self.automata.add_state( state )
        for edgeID, edge in edgesList.items():
            self.automata.add_edge( edge )

    def parseTraceSet(self, sessionFile):
        traceAmount = int( self.taskJson['traceAmount'] )
        for i in range(traceAmount):
            # check TraceSet folder
            traceSetFile = os.path.join(sessionFile, 'traceSet', str(i+1))
            if not os.path.exists( traceSetFile ):
                raise Exception('Cannot find traceSet-',traceSetFile)

            traceTxtFile = os.path.join(sessionFile, 'traceSet', str(i+1), 'trace.txt')
            if not os.path.exists( traceSetFile ):
                raise Exception('Cannot find trace.txt : ',traceTxtFile)

            self.loadTraceSet(sessionFile, traceTxtFile, i)

    def loadTraceSet(self, sessionFile, traceTxtFile, i):
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
                        state = self.automata.get_state_byId(NodeID)
                        state.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['states'].append( state )

                # check if is edge
                elif NodeFile.endswith('.json'):
                    if self.automata.has_edgeID(NodeID):
                        edge = self.automata.get_edge_byId(NodeID)
                        edge.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['edges'].append( edge )
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
                if self.automata.has_stateID( stateID ):
                    self.automata.get_state_byId(stateID).add_keyword('label', node.label)
        for branch in t3a.branches:
            if self.automata.has_edgeID( branch.actionIdx ):
                self.automata.get_edge_byId( branch.actionIdx ).add_keyword('label', branch.label)

    def reset(self):
        self.automata   = None
        self.traces     = []
        self.taskJson   = None
        self.edgesJson  = None
 
    def getAutomata(self):
        return self.automata

    def getTraces(self):
        return self.traces