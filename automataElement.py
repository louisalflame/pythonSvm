#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json

from tracePath import Path

class AutomataElement:
    def __init__(self):
        # basic
        self.edges = []
        self.states = []
        # vector
        self.keywords = {}
        self.actions = []
        self.orders = {}

    def add_state(self, state):
        if state not in self.states:
            self.states.append( state )
            for key, keyword in state.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = [ keyword ]
                elif keyword not in self.keywords[key]:
                    self.keywords[key].append( keyword )

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append( edge )
            # add actions
            if edge.get_symbol() not in self.actions:
                self.actions.append( edge.get_symbol() )

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

    def get_keywords(self):
        return self.keywords

    def get_actions(self):
        return self.actions

    def get_vector(self):
        vector = []
        vectorStr = ""
        # add keywords
        for key, keywords in self.keywords.items():
            for keyword in keywords:
                vector.append( str(key)+'_'+str(keyword) )

        # add actions
        for action in self.actions:
            vector.append( action )

        vector = [ str(index+1)+':'+str(value) for index, value in enumerate(vector) ]
        vectorStr = ' '.join(vector) + '\n'
        return vectorStr        

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

    def reset(self):
        self.states = []
        self.edges = []
        self.keywords = {}
        self.actions = {}
        self.orders = {}
        self.automata = None

    def add_state(self, state):
        self.states.append( state )
        for key, keyword in state.get_keywords().items():
            if key not in self.keywords:
                self.keywords[key] = { keyword : 1 }
            elif keyword in self.keywords[key]:
                self.keywords[key][keyword] += 1
            else:
                self.keywords[key][keyword] = 1

    def add_edge(self, edge, index):
        self.edges.append(edge)
        edgeSymbol = edge.get_symbol()
        if edgeSymbol in self.actions:
            self.actions[edgeSymbol]['count'] += 1
            self.actions[edgeSymbol]['index'].append( index )
        elif edgeSymbol not in self.actions:
            self.actions[edgeSymbol] = {  'count' : 1,
                                          'index' : [ index ] }

    def set_automata(self, automata):
        self.automata = automata

    def make_vector_string(self):
        if not self.automata: 
            return ""

        vector = []
        vectorStr = ""
        # add keywords
        for key, keywords in self.automata.get_keywords().items():
            for keyword in keywords:
                if key in self.keywords and keyword in self.keywords[key]:
                    vector.append( self.keywords[key][keyword] )
                elif key in self.keywords and keyword not in self.keywords[key]:
                    vector.append( 0 )
                else:
                    vector.append( 0 )

        # add actions
        for action in self.automata.get_actions():
            if action in self.actions:
                vector.append( self.actions[action]['count'] )
            else:
                vector.append( 0 )

        # add orders

        vector = [ str(index+1)+':'+str(value) for index, value in enumerate(vector) ]
        vectorStr = ' '.join(vector) + '\n'
        return vectorStr

class StateElement:
    def __init__(self):
        self.id = None
        self.xmlFile = None
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

    def set_xml(self, xmlFile):
        self.xmlFile = xmlFile 

    def get_symbol(self):
        """TODO: """
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

    def get_symbol(self):
        symbolFrom = self.stateFrom.get_symbol()
        symbolTo   = self.stateTo.get_symbol()
        symbol = str(symbolFrom)+'>'+str(symbolTo)+'ID:'+str(self.id)+'N:'+str(self.name)+'XPath:'+str(self.xpath)
        return symbol