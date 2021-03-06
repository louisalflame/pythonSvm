#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, enum

from tracePath import Path
from labelDictionary import LabelDictionary

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

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append( edge )

    def get_states(self):
        return self.states

    def get_edges(self):
        return self.edges

    def get_state_byId(self, stateID):
        for state in self.states:
            if str(state.get_id()) == str(stateID):
                return state
        return None

    def get_edge_byId(self, edgeID):
        for edge in self.edges:
            if str(edge.get_id()) == str(edgeID):
                return edge
        return None

    def get_edges_byFromTo(self, stateFrom, stateTo):
        edges = []
        for edge in self.edges:
            if str(edge.get_stateFrom().get_id()) == str(stateFrom) and \
               str(edge.get_stateTo().get_id()  ) == str(stateTo  ):
                edges.append(edge)
        return edges

    def has_stateID(self, stateID):
        for state in self.states:
            if str(state.get_id()) == str(stateID):
                return True
        return False

    def has_edgeID(self, edgeID):
        for edge in self.edges:
            if str(edge.get_id()) == str(edgeID):
                return True
        return False

    def remake_keywords(self):
        for state in self.states:
            for key, keywords in state.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = keywords
                else:
                    for keyword in keywords:
                        if keyword not in self.keywords[key]:
                            self.keywords[key].append( keyword )

        for edge in self.edges:
            for key, keywords in state.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = keywords
                else:
                    for keyword in keywords:
                        if keyword not in self.keywords[key]:
                            self.keywords[key].append( keyword )

            if edge.get_symbol() not in self.actions:
                self.actions.append( edge.get_symbol() )

    def get_keywords(self):
        return self.keywords

    def get_actions(self):
        return self.actions

    def use_label_dictionary(self):
        LabelDictionary.parseLabel()
        labels = LabelDictionary.getLabelDictionary()

        for label in labels['screen']:
            if 'label' not in self.keywords:
                self.keywords['label'] = [ label.getLabel() ]
            elif label.getLabel() not in self.keywords['label']:
                self.keywords['label'].append( label.getLabel() )

        for label in labels['action']:
            if 'label' not in self.keywords:
                self.keywords['label'] = [ label.getLabel() ]
            elif label.getLabel() not in self.keywords['label']:
                self.keywords['label'].append( label.getLabel() )

    def get_vector(self, needs):
        vector = []
        vectorStr = ""
        # add keywords
        for key, keywords in self.keywords.items():
            if needs and key not in needs:
                continue

            for keyword in keywords:
                vector.append( str(key)+'_'+str(keyword) )

        # add actions
        # for action in self.actions:
        #    vector.append( action )

        vector = [ str(index+1)+':<'+str(value)+'>' for index, value in enumerate(vector) ]
        vectorStr = '\n'.join(vector) + '\n'
        return vectorStr        

class TraceElement:
    def __init__(self):
        # basic
        self.label = TraceLabel.UNLABELED
        self.states = []
        self.edges = []
        # vector
        self.keywords = {}
        # automata
        self.automata = None

    def reset(self):
        self.states = []
        self.edges = []
        self.keywords = {}
        self.automata = None

    def set_label(self, label):
        self.label = label

    def add_state(self, state):
        self.states.append( state )

    def add_edge(self, edge, index):
        self.edges.append( (edge, index) )

    def set_automata(self, automata):
        self.automata = automata
        self.remake_keywords()

    def remake_keywords(self):
        self.keywords = {}
        for state in self.states:
            for key, keywords in state.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = {}
                    for keyword in keywords:
                        self.keywords[key][keyword] = 1
                else:
                    for keyword in keywords:
                        if keyword in self.keywords[key]:
                            self.keywords[key][keyword] += 1
                        else:
                            self.keywords[key][keyword] = 1

        for edge, index in self.edges:
            for key, keywords in edge.get_keywords().items():
                if key not in self.keywords:
                    self.keywords[key] = {}
                    for keyword in keywords:
                        self.keywords[key][keyword] = 1
                else:
                    for keyword in keywords:
                        if keyword in self.keywords[key]:
                            self.keywords[key][keyword] += 1
                        else:
                            self.keywords[key][keyword] = 1

    def make_vector_string(self, needs ):
        if not self.automata: 
            return ""

        vector = []
        vectorStr = ""
        # add keywords
        for key, keywords in self.automata.get_keywords().items():
            if needs and key not in needs:
                continue

            for keyword in keywords:
                if key in self.keywords and keyword in self.keywords[key]:
                    vector.append( self.keywords[key][keyword] )
                elif key in self.keywords and keyword not in self.keywords[key]:
                    vector.append( 0 )
                else:
                    vector.append( 0 )

        vector = [ str(index+1)+':'+str(value) for index, value in enumerate(vector) ]

        vectorStr = str(self.label) + ' ' + ' '.join(vector) + '\n'

        return vectorStr

class StateElement:
    def __init__(self):
        self.id = None
        self.xmlFile = None
        self.keywords = {}

    def add_keyword(self, key, keyword):
        if key not in self.keywords:
            self.keywords[key] = [ keyword ]
        else:
            self.keywords[key].append( keyword )

    def get_keywords(self):
        return self.keywords

    def set_id(self, id):
        self.id = str(id)

    def get_id(self):
        return self.id

    def set_xml(self, xmlFile):
        self.xmlFile = xmlFile 

    def get_xml(self):
        return self.xmlFile

    def get_symbol(self):
        """TODO: """
        return self.id

class EdgeElement:
    def __init__(self):
        self.id        = None
        self.attr      = {}
        self.stateFrom = None
        self.stateTo   = None
        self.xml       = None
        self.keywords = {}

    def add_keyword(self, key, keyword):
        if key not in self.keywords:
            self.keywords[key] = [ keyword ]
        else:
            self.keywords[key].append( keyword )
            
    def get_keywords(self):
        return self.keywords

    def set_id(self, id):
        self.id = str(id)

    def get_id(self):
        return self.id

    def set_stateFrom(self, stateFrom):
        self.stateFrom = stateFrom

    def set_stateTo(self, stateTo):
        self.stateTo = stateTo

    def get_stateFrom(self):
        return self.stateFrom

    def get_stateTo(self):
        return self.stateTo

    def set_xml(self, xmlFile):
        self.xmlFile = xmlFile 

    def get_symbol(self):
        symbolFrom = self.stateFrom.get_symbol()
        symbolTo   = self.stateTo.get_symbol()
        symbol = str(symbolFrom)+'=>'+str(symbolTo)

        for w in [ 'id', 'name', 'xpath', 'label' ]:
            if w in self.keywords:
                for v in self.keywords[w]:
                    symbol += str( v )

        return symbol

class TraceLabel:
    PASS      = 0
    FAIL      = 1
    UNLABELED = 2
    CRASH     = 3
    WRONG     = 4
    UNKNOWN   = 5

    @classmethod            
    def parse(cls, key):
        key = ''.join(key.split()).upper() 
        if key == 'UNLABELED':
            return cls.UNLABELED
        elif key == 'PASS':
            return cls.PASS
        elif key == 'UNKNOWN':
            return cls.UNKNOWN
        elif key == 'CRASH':
            return cls.CRASH
        elif key == 'WRONG':
            return cls.WRONG
        else:
            return cls.UNKNOWN